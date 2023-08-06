PsProfile
=========

A python process profiler.  Watches a process tree and emits resource usage metrics.  Uses the psutil library, so runs on a mac and linux (haven't tested Windows,
but theoretically it will work).  You will get slightly different fields back depending on the operating system.
Used by the `Cosmos Workflow Management System <https://cosmos.hms.harvard.edu/>`_.


Install
========

pip install psprofile

Usage
=====

.. code-block:: bash

    $ psprofile -h
    usage: psprofile [-h] [-o OUTPUT_FILE] [-i POLL_INTERVAL] [-w WAIT] ...

    Profile resource usage of a command

    positional arguments:
      command               The command to run.

    optional arguments:
      -h, --help            show this help message and exit
      -o OUTPUT_FILE, --output_file OUTPUT_FILE
                            File to store output of profile to.
      -i POLL_INTERVAL, --poll_interval POLL_INTERVAL
                            How often to poll the resource usage information in
                            /proc, in seconds (default 1).
      -w WAIT, --wait WAIT  time to wait for executable to exist

    $ psprofile ls $HOME
    $ psprofile python test.py
    $ psprofile "echo hi; sleep ls"

    # note that:
    $ psprofile echo hi > tmp/test  #  (psprofile's output is redirected)
    # is not the same as:
    $ psprofile "echo hi > /tmp/test" #  (echo's output is redirected)

Example output:

.. code-block:: bash

    $ psprofile /path/to/bash.script

.. code-block:: json

        {
            "avg_num_threads": 1,
            "cpu_time": 0,
            "avg_vms_mem_kb": 11427840,
            "io_read_kb": 4096,
            "io_write_kb": 0,
            "max_num_threads": 1,
            "system_time": 0,
            "max_rss_mem_kb": 1470464,
            "percent_cpu": 0,
            "max_vms_mem_kb": 11427840,
            "wall_time": 2,
            "ctx_switch_voluntary": 12,
            "user_time": 0,
            "avg_num_fds": 4,
            "num_polls": 1,
            "max_num_fds": 4,
            "io_write_count": 0,
            "avg_rss_mem_kb": 1470464,
            "ctx_switch_involuntary": 3,
            "io_read_count": 12,
            "exit_status": 0
        }