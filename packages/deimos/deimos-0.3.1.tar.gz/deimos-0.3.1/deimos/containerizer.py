import base64
import errno
from fcntl import LOCK_EX, LOCK_NB, LOCK_SH, LOCK_UN
import inspect
import logging
import os
import random
import re
import signal
import subprocess
import sys
import threading
import time

try:                  # Prefer system installation of Mesos protos if available
    from mesos_pb2 import *
    from containerizer_pb2 import *
except:
    from deimos.mesos_pb2 import *
    from deimos.containerizer_pb2 import *

import deimos.cgroups
from deimos.cmd import Run
import deimos.config
import deimos.containerizer
import deimos.docker
from deimos.err import Err
import deimos.logger
from deimos.logger import log
import deimos.mesos
import deimos.path
from deimos.proto import recordio
from deimos._struct import _Struct
import deimos.state
import deimos.sig


class Containerizer(object):
    def __init__(self): pass
    def launch(self, *args): pass
    def update(self, *args): pass
    def usage(self, *args): pass
    def wait(self, *args): pass
    def destroy(self, *args): pass
    def recover(self, *args): pass
    def containers(self, *args): pass
    def __call__(self, *args):
        try:
            name   = args[0]
            method = { "launch"     : self.launch,
                       "update"     : self.update,
                       "usage"      : self.usage,
                       "wait"       : self.wait,
                       "destroy"    : self.destroy,
                       "recover"    : self.recover,
                       "containers" : self.containers }[name]
        except IndexError:
            raise Err("Please choose a subcommand")
        except KeyError:
            raise Err("Subcommand %s is not valid for containerizers" % name)
        return method(*args[1:])

def methods():
    "Names of operations provided by containerizers, as a set."
    pairs = inspect.getmembers(Containerizer, predicate=inspect.ismethod)
    return set( k for k, _ in pairs if k[0:1] != "_" )

class Docker(Containerizer, _Struct):
    def __init__(self, workdir="/tmp/mesos-sandbox",
                       state_root="/tmp/deimos",
                       shared_dir="fs",
                       optimistic_unpack=True,
                       container_settings=deimos.config.Containers(),
                       index_settings=deimos.config.DockerIndex()):
        _Struct.__init__(self, workdir=workdir,
                               state_root=state_root,
                               shared_dir=shared_dir,
                               optimistic_unpack=optimistic_unpack,
                               container_settings=container_settings,
                               index_settings=index_settings,
                               runner=None,
                               state=None)
    def launch(self, *args):
        log.info(" ".join(args))
        fork = False if "--no-fork" in args else True
        deimos.sig.install(self.log_signal)
        run_options = []
        proto = recordio.read(Launch)
        launchy = deimos.mesos.Launch(proto)
        state = deimos.state.State(self.state_root,
                                   mesos_id=launchy.container_id)
        state.push()
        lk_l = state.lock("launch", LOCK_EX)
        state.executor_id = launchy.executor_id
        state.push()
        state.ids()
        mesos_directory() # Redundant?
        if launchy.directory:
            os.chdir(launchy.directory)
        # TODO: if launchy.user:
        #           os.seteuid(launchy.user)
        url, options = self.container_settings.override(*launchy.container)
        pre, image = re.split(r"^docker:///?", url)
        if pre != "":
            raise Err("URL '%s' is not a valid docker:// URL!" % url)
        if image == "":
            image = self.default_image(launchy)
        log.info("image  = %s", image)
        run_options += [ "--sig-proxy" ]
        run_options += [ "--rm" ]     # This is how we ensure container cleanup
        run_options += [ "--cidfile", state.resolve("cid") ]

        place_uris(launchy, self.shared_dir, self.optimistic_unpack)
        run_options += [ "-w", self.workdir ]

        # Docker requires an absolute path to a source filesystem, separated
        # from the bind path in the container with a colon, but the absolute
        # path to the Mesos sandbox might have colons in it (TaskIDs with
        # timestamps can cause this situation). So we create a soft link to it
        # and mount that.
        shared_full = os.path.abspath(self.shared_dir)
        sandbox_symlink = state.sandbox_symlink(shared_full)
        run_options += [ "-v", "%s:%s" % (sandbox_symlink, self.workdir) ]

        cpus, mems = launchy.cpu_and_mem
        env = launchy.env
        run_options += options

        # We need to wrap the call to Docker in a call to the Mesos executor
        # if no executor is passed as part of the task. We need to pass the
        # MESOS_* environment variables in to the container if we're going to
        # start an executor.
        observer_argv = None
        if launchy.needs_observer:
            # NB: The "@@docker@@" variant is a work around for Mesos's option
            # parser. There is a fix in the pipeline.
            observer_argv = [ mesos_executor(), "--override",
                              deimos.path.me(), "wait", "@@observe-docker@@" ]
            state.lock("observe", LOCK_EX|LOCK_NB) ####### Explanation of Locks
            # When the observer is running, we would like its call to wait()
            # to finish before all others; and we'd like the observer to have
            # a chance to report TASK_FINISHED before the calls to wait()
            # report their results (which would result in a TASK_FAILED).
            #
            # For this reason, we take the "observe" lock in launch(), before
            # we call the observer and before releasing the "launch" or "wait"
            # locks.
            #
            # Calls to wait() in observer mode will actually skip locking
            # "observe"; but other wait calls must take this lock. The
            # "observe" lock is held by launch() until the observer executor
            # completes, at which point we can be reasonably sure its status
            # was propagated to the Mesos slave.
        else:
            env += mesos_env() + [("MESOS_DIRECTORY", self.workdir)]

        runner_argv = deimos.docker.run(run_options, image, launchy.argv,
                                        env=env, ports=launchy.ports,
                                        cpus=cpus, mems=mems)

        log_mesos_env(logging.DEBUG)

        observer = None
        with open("stdout", "w") as o:        # This awkward multi 'with' is a
            with open("stderr", "w") as e:    # concession to 2.6 compatibility
                with open(os.devnull) as devnull:
                    log.info(deimos.cmd.present(runner_argv))
                    self.runner = subprocess.Popen(runner_argv, stdin=devnull,
                                                                stdout=o,
                                                                stderr=e)
                    state.pid(self.runner.pid)
                    state.await_cid()
                    state.push()
                    lk_w = state.lock("wait", LOCK_EX)
                    lk_l.unlock()
                    if fork:
                        pid = os.fork()
                        if pid is not 0:
                            state.ids()
                            log.info("Forking watcher into child...")
                            return
                    state.ids()
                    if observer_argv is not None:
                        observer_argv += [state.cid()]
                        log.info(deimos.cmd.present(observer_argv))
                        call = deimos.cmd.in_sh(observer_argv, allstderr=False)
                        # TODO: Collect these leaking file handles.
                        obs_out = open(state.resolve("observer.out"), "w+")
                        obs_err = open(state.resolve("observer.err"), "w+")
                        # If the Mesos executor sees LIBPROCESS_PORT=0 (which
                        # is passed by the slave) there are problems when it
                        # attempts to bind. ("Address already in use").
                        # Purging both LIBPROCESS_* net variables, to be safe.
                        for v in ["LIBPROCESS_PORT", "LIBPROCESS_IP"]:
                            if v in os.environ:
                                del os.environ[v]
                        observer = subprocess.Popen(call, stdin=devnull,
                                                          stdout=obs_out,
                                                          stderr=obs_err,
                                                          close_fds=True)
        data = Run(data=True)(deimos.docker.wait(state.cid()))
        state.exit(data)
        lk_w.unlock()
        for p, arr in [(self.runner, runner_argv), (observer, observer_argv)]:
            if p is None:
                continue
            thread = threading.Thread(target=p.wait)
            thread.start()
            thread.join(10)
            if thread.is_alive():
                log.warning(deimos.cmd.present(arr, "SIGTERM after 10s"))
                p.terminate()
            thread.join(1)
            if thread.is_alive():
                log.warning(deimos.cmd.present(arr, "SIGKILL after 1s"))
                p.kill()
            msg = deimos.cmd.present(arr, p.wait())
            if p.wait() == 0:
                log.info(msg)
            else:
                log.warning(msg)
        return state.exit()
    def update(self, *args):
        log.info(" ".join(args))
        log.info("Update is a no-op for Docker...")
    def usage(self, *args):
        log.info(" ".join(args))
        message = recordio.read(Usage)
        container_id = message.container_id.value
        state = deimos.state.State(self.state_root, mesos_id=container_id)
        state.await_launch()
        state.ids()
        if state.cid() is None:
            log.info("Container not started?")
            return 0
        if state.exit() is not None:
            log.info("Container is stopped")
            return 0
        cg = deimos.cgroups.CGroups(**deimos.docker.cgroups(state.cid()))
        if len(cg.keys()) == 0:
            log.info("Container has no CGroups...already stopped?")
            return 0
        try:
            recordio.write(ResourceStatistics,
                           timestamp             = time.time(),
                           mem_limit_bytes       = cg.memory.limit(),
                           cpus_limit            = cg.cpu.limit(),
                         # cpus_user_time_secs   = cg.cpuacct.user_time(),
                         # cpus_system_time_secs = cg.cpuacct.system_time(),
                           mem_rss_bytes         = cg.memory.rss())
        except AttributeError as e:
            log.error("Missing CGroup!")
            raise e
        return 0
    def wait(self, *args):
        log.info(" ".join(args))
        observe = False
        # NB: The "@@observe-docker@@" variant is a work around for Mesos's
        #     option parser. There is a fix in the pipeline.
        if list(args[0:1]) in [ ["--observe-docker"], ["@@observe-docker@@"] ]:
            # In Docker mode, we use Docker wait to wait for the container
            # and then exit with the returned exit code. The Docker CID is
            # passed on the command line.
            state = deimos.state.State(self.state_root, docker_id=args[1])
            observe = True
        else:
            message = recordio.read(Wait)
            container_id = message.container_id.value
            state = deimos.state.State(self.state_root, mesos_id=container_id)
        self.state = state
        deimos.sig.install(self.stop_docker_and_resume)
        state.await_launch()
        try:
            if not observe:
                state.lock("observe", LOCK_SH, seconds=None)
            state.lock("wait", LOCK_SH, seconds=None)
        except IOError as e:                       # Allows for signal recovery
            if e.errno != errno.EINTR:
                raise e
            if not observe:
                state.lock("observe", LOCK_SH, seconds=1)
            state.lock("wait", LOCK_SH, seconds=1)
        termination = (state.exit() if state.exit() is not None else 64) << 8
        recordio.write(Termination,
                       killed  = False,
                       message = "",
                       status  = termination)
        if state.exit() is not None:
            return state.exit()
        raise Err("Wait lock is not held nor is exit file present")
    def destroy(self, *args):
        log.info(" ".join(args))
        message = recordio.read(Destroy)
        container_id = message.container_id.value
        state = deimos.state.State(self.state_root, mesos_id=container_id)
        state.await_launch()
        lk_d = state.lock("destroy", LOCK_EX)
        if state.exit() is None:
            Run()(deimos.docker.stop(state.cid()))
        else:
            log.info("Container is stopped")
        return 0
    def containers(self, *args):
        log.info(" ".join(args))
        data = Run(data=True)(deimos.docker.docker("ps", "--no-trunc", "-q"))
        mesos_ids = []
        for line in data.splitlines():
            cid = line.strip()
            state = deimos.state.State(self.state_root, docker_id=cid)
            if not state.exists():
                continue
            try:
                state.lock("wait", LOCK_SH|LOCK_NB)
            except deimos.flock.Err:     # LOCK_EX held, so launch() is running
                mesos_ids += [state.mesos_container_id()]
        containers = Containers()
        for mesos_id in mesos_ids:
            container = containers.containers.add()
            container.value = mesos_id
        recordio.writeProto(containers)
        return 0
    def log_signal(self, signum):
        pass
    def stop_docker_and_resume(self, signum):
        if self.state is not None and self.state.cid() is not None:
            cid = self.state.cid()
            log.info("Trying to stop Docker container: %s", cid)
            try:
                Run()(deimos.docker.stop(cid))
            except subprocess.CalledProcessError:
                pass
            return deimos.sig.Resume()
    def default_image(self, launchy):
        opts = dict(self.index_settings.items(onlyset=True))
        if "account_libmesos" in opts:
            if not launchy.needs_observer:
                opts["account"] = opts["account_libmesos"]
            del opts["account_libmesos"]
        return deimos.docker.matching_image_for_host(**opts)

####################################################### Mesos interface helpers

MESOS_ESSENTIAL_ENV = [ "MESOS_SLAVE_ID",     "MESOS_SLAVE_PID",
                        "MESOS_FRAMEWORK_ID", "MESOS_EXECUTOR_ID",
                        "MESOS_CHECKPOINT",   "MESOS_RECOVERY_TIMEOUT" ]

def mesos_env():
    env = os.environ.get
    return [ (k, env(k)) for k in MESOS_ESSENTIAL_ENV if env(k) ]

def log_mesos_env(level=logging.INFO):
    for k, v in os.environ.items():
        if k.startswith("MESOS_") or k.startswith("LIBPROCESS_"):
            log.log(level, "%s=%s" % (k, v))

def mesos_directory():
    if not "MESOS_DIRECTORY" in os.environ: return
    work_dir = os.path.abspath(os.getcwd())
    task_dir = os.path.abspath(os.environ["MESOS_DIRECTORY"])
    if task_dir != work_dir:
        log.info("Changing directory to MESOS_DIRECTORY=%s", task_dir)
        os.chdir(task_dir)

def mesos_executor():
    return os.path.join(os.environ["MESOS_LIBEXEC_DIRECTORY"],
                        "mesos-executor")

def mesos_default_image():
    return os.environ.get("MESOS_DEFAULT_CONTAINER_IMAGE")

def place_uris(launchy, directory, optimistic_unpack=False):
    cmd = deimos.cmd.Run()
    cmd(["mkdir", "-p", directory])
    for item in launchy.uris:
        uri = item.value
        gen_unpack_cmd = unpacker(uri) if optimistic_unpack else None
        log.info("Retrieving URI: %s", deimos.cmd.escape([uri]))
        try:
            basename = uri.split("/")[-1]
            f = os.path.join(directory, basename)
            if basename == "":
                raise IndexError
        except IndexError:
            log.info("Not able to determine basename: %r", uri)
            continue
        try:
            cmd(["curl", "-sSfL", uri, "--output", f])
        except subprocess.CalledProcessError as e:
            log.warning("Failed while processing URI: %s",
                        deimos.cmd.escape(uri))
            continue
        if item.executable:
            os.chmod(f, 0755)
        if gen_unpack_cmd is not None:
            log.info("Unpacking %s" % f)
            cmd(gen_unpack_cmd(f, directory))
            cmd(["rm", "-f", f])

def unpacker(uri):
    if re.search(r"[.](t|tar[.])(bz2|xz|gz)$", uri):
        return lambda f, directory: ["tar", "-C", directory, "-xf", f]
    if re.search(r"[.]zip$", uri):
        return lambda f, directory: ["unzip", "-d", directory, f]

