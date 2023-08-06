Cassandra Quickstart
====================

This tool downloads Cassandra, Java, ccm, and drivers into your home
directory (~/.cassandra-quickstart) and starts a single node Cassandra
cluster. This is meant to be useful for protyping and development
tasks, not for production.

The idea is to have a one-liner to install everything you need to use
Cassandra on Linux, Mac OSX, or Windows. The only requirement is that
you have Python installed (2.7 tested) which every Linux and Mac
system should have pre-installed. In the future I plan to distribute
an .exe for Windows that bundles all the requirements.

**Windows is currently broken in this 0.1 release.**

Install
--------

    easy_install cassandra-quickstart

One line to create and start a cluster
--------------------------------------

    cassandra-quickstart install

Commands
--------

.. code::

    usage: cassandra-quickstart [-h] [--config CONFIG_DIRECTORY] [--name CLUSTER_NAME]
           {install,destroy,start,stop,cqlsh,nodetool,status,help} ...

    Cassandra Quickstart
    
    positional arguments:
      {install,destroy,start,stop,cqlsh,nodetool,status,help}
        install             Install Cassandra
        destroy             Remove Cassandra
        start               Start Cassandra
        stop                Stop Cassandra
        cqlsh               Cassandra Shell
        nodetool            Cassandra node management tool (ex: nodetool ring)
        status              Print status of cluster
    
    optional arguments:
      -h, --help            show this help message and exit
      --config CONFIG_DIRECTORY
                            Configuration directory (default is ~/.cassandra-
                            quickstart)
      --name CLUSTER_NAME   Name of the cluster to operate on (default is
                            'cassandra')
