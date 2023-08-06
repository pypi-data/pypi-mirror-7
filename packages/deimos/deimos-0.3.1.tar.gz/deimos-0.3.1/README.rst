======
deimos
======

Deimos is a Docker plugin for Mesos, providing external containerization as
described in `MESOS-816`_.

**NOTE**: Deimos is currently under heavy development and relies on very recent
changes in Mesos master that have not been released yet. Be prepared for some
bumps and changing APIs. If you run into trouble, please file an issue on
Github.  Official support for external containerizers like Deimos will be
available in the next Mesos release (0.19), at which point there will be a
stable release of Deimos as well.

------------
Installation
------------

For a complete installation walkthrough, see `this Gist`_.

Deimos can be installed `from the Cheeseshop`_.

.. code-block:: bash

    pip install deimos

Although Deimos does not have a library dependency on a particular Mesos
version, one does need a development version of the `Mesos package`_ (for which
there are also `Python bindings`_), available only for very recent Ubuntu, to
try out external containerizers. If you want to use Deimos together with
Marathon, please use `this patched Marathon`_. Official support for external
containerizers will be available in the next Mesos release (0.19).

----------------------------
Passing Parameters to Docker
----------------------------

In Mesos, every successful resource offer is ultimately followed up with a
``TaskInfo`` that describes the work to be done. Within the ``TaskInfo`` is a
``CommandInfo`` and within the ``CommandInfo`` there is a ``ContainerInfo``
(following `MESOS-816`_). The ``ContainerInfo`` structure allows specification
of an *image URL* and *container options*. For example:

.. code-block:: c

    {
      container = ContainerInfo {
        image = "docker:///ubuntu"
        options = ["-c", "10240"]
      }
    }

Deimos handles image URLs beginning with ``docker:///`` by stripping the
prefix and using the remainder as the image name. The container options are
passed to ``docker run`` when the task is launched.

If no ``ContainerInfo`` is present in a task, Deimos will still containerize
it, by using the ``--default_container_image`` passed to the slave, or taking
a reasonable guess based on the host's distribution and release.

Some options for Docker, like ``-H``, do not apply only to ``docker run``.
These options should be set in the Deimos configuration file.

Deimos recognizes Mesos resources that specify ports, CPUs and memory and
translates them to appropriate Docker options.


-------
Logging
-------

Deimos logs to the console when run interactively and to syslog when run in the
background. You can configure logging explicitly in the Deimos configuration
file.


-------------
Configuration
-------------

There is an example configuration file in ``example.cfg`` which documents all
the configuration options. The two config sections that are likely to be most
important in production are:

* ``[docker]``: global Docker options (``--host``)

* ``[log]``: logging settings

Configuration files are searched in this order:

.. code-block:: bash

    ./deimos.cfg
    ~/.deimos
    /etc/deimos.cfg
    /usr/etc/deimos.cfg
    /usr/local/etc/deimos.cfg

Only one configuration file -- the first one found -- is loaded. To see what
Deimos thinks its configuration is, run ``deimos config``.


-------------------
The State Directory
-------------------

Deimos creates a state directory for each container, by default under
``/tmp/deimos``, where it tracks the container's status, start time and PID.
File locks are maintained for each container to coordinate invocations of
Deimos that start, stop and probe the container.

To clean up state directories belonging to exited containers, invoke Deimos
as follows:

.. code-block:: bash

    deimos state --rm

This task can be run safely from Cron at a regular interval. In the future,
Deimos will not require separate invocation of the ``state`` subcommand for
regular operation.


-------------------------------
Configuring Mesos To Use Deimos
-------------------------------

Only the slave needs to be configured. Set these options:

.. code-block:: bash

    --containerizer_path=/usr/local/bin/deimos --isolation=external

The packaged version of Mesos can also load these options from files:

.. code-block:: bash

    echo /usr/local/bin/deimos    >    /etc/mesos-slave/containerizer_path
    echo external                 >    /etc/mesos-slave/isolation


.. _`from the Cheeseshop`: https://pypi.python.org/pypi/deimos

.. _MESOS-816: https://issues.apache.org/jira/browse/MESOS-816

.. _`Mesos package`: http://downloads.mesosphere.io/master/ubuntu/13.10/mesos_0.19.0-xcon2_amd64.deb

.. _`Python bindings`: http://downloads.mesosphere.io/master/ubuntu/13.10/mesos_0.19.0-xcon2_amd64.egg

.. _`this Gist`: https://gist.github.com/solidsnack/10944095

.. _`this patched Marathon`: http://downloads.mesosphere.io/marathon/marathon_0.5.0-xcon2_noarch.deb
