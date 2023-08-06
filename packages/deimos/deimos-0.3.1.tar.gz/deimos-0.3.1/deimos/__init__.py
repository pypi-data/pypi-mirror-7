#!/usr/bin/env python
import calendar
import os
import signal
import subprocess
import sys
import time

import deimos.cleanup
import deimos.config
import deimos.containerizer
from deimos.err import Err
import deimos.flock
from deimos.logger import log
import deimos.sig
import deimos.usage


def cli(argv=None):
    deimos.sig.install(lambda _: None)
    if argv is None: argv = sys.argv
    sub = argv[1] if len(argv) > 1 else None

    if sub in ["-h", "--help", "help"]:
        print format_help()
        return 0

    conf = deimos.config.load_configuration()

    if sub == "config":
        log.info("Final configuration:")
        for _, conf in conf.items():
            print "%r" % conf
        return 0

    if sub == "locks":
        deimos.flock.lock_browser(os.path.join(conf.state.root, "mesos"))
        return 0

    if sub == "state":
        cleanup = deimos.cleanup.Cleanup(conf.state.root)
        t, rm   = time.time(), False
        for arg in argv[2:]:
            if arg == "--rm":
                rm = True
                continue
            t = calendar.timegm(time.strptime(arg, "%Y-%m-%dT%H:%M:%SZ"))
        if rm:
            return cleanup.remove(t)
        else:
            for d in cleanup.dirs(t):
                sys.stdout.write(d + "\n")
            return 0

    if sub not in deimos.containerizer.methods():
        print >>sys.stderr, format_help()
        print >>sys.stderr, "** Please specify a subcommand **".center(79)
        log.error("Bad ARGV: %r" % argv[1:])
        return 1

    deimos.docker.options = conf.docker.argv()
    containerizer = deimos.containerizer.Docker(
        container_settings=conf.containers,
        optimistic_unpack=conf.uris.unpack,
        state_root=conf.state.root
    )

    deimos.usage.report()
    try:
        result = containerizer(*argv[1:])
        deimos.usage.report()
        if result is not None:
            if isinstance(result, int):
                return result
            if isinstance(result, str):
                sys.stdout.write(result)
            else:
                for item in result:
                    sys.stdout.write(str(item) + "\n")
    except Err as e:
        log.error("%s.%s: %s", type(e).__module__, type(e).__name__, str(e))
        return 4
    except subprocess.CalledProcessError as e:
        log.error(str(e))
        return 4
    except Exception:
        log.exception("Unhandled failure in %s", sub)
        return 8
    return 0

def format_help():
    return """
 USAGE: deimos launch  (--no-fork)?
        deimos usage
        deimos destroy
        deimos wait    (--docker <docker-id>)?
        deimos locks
        deimos state

  Deimos provides Mesos integration for Docker, allowing Docker to be used as
  an external containerizer.

 deimos launch (--no-fork)?

  Launches a container and runs the executor or command specified in the
  TaskInfo, passed in on standard in.

  The launch subcommand always watches the launched container and logs changes
  in its lifecycle. By default, it forks off a child to do the watching, as
  part of the contract external containerizers have with Mesos. With
  --no-fork, launch will watch the container and log in the foreground. This
  can be helpful during debugging.

 deimos usage

  Generates a protobuf description of the resources used by the container.

 deimos destroy

  Shuts down the specified container.

 deimos wait (--docker <docker-id>)?

  Without --docker, reads STDIN to find the container to watch.

  With --docker, waits for a particular Docker CID to exit and records the
  result in the state directory, returning an appropriate exit code.

 deimos locks

  List file locks taken by Deimos, associating each file with a PID, an inode,
  and a lock level. The same file may appear multiple times.

 deimos state (--rm)?

  List stale state directories (those with an exit file). With --rm, removes
  stale states.

 deimos config

  Load and display the configuration.

""".strip("\n")

if __name__ == "__main__":
    sys.exit(cli(sys.argv))

