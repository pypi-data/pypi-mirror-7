Mistral
=======

Task Orchestration and Scheduling service for OpenStack cloud


Installation
------------

First of all, in a shell run:

    tox

This will install necessary virtual environments and run all the project tests. Installing virtual environments may take significant time (~10-15 mins).

Running Mistral API server
--------------------------

To run Mistral API server perform the following command in a shell:

    tox -evenv -- python mistral/cmd/launch.py --server api --config-file path_to_config*

Note that an example configuration file can be found in etc/mistral.conf.example.

Running Mistral Engines
-----------------------

To run Mistral Engine perform the following command in a shell:

    tox -evenv -- python mistral/cmd/launch.py --server engine --config-file path_to_config*

Running Mistral Task Executors
------------------------------
To run Mistral Task Executor instance perform the following command in a shell:

    tox -evenv -- python mistral/cmd/launch.py --server executor --config-file path_to_config

Note that at least one Engine instance and one Executor instance should be running so that workflow tasks are processed by Mistral.

Debugging
---------

To debug using a local engine and executor without dependencies such as RabbitMQ, create etc/mistral.conf with the following settings::

    [DEFAULT]
    rpc_backend = fake

    [pecan]
    auth_enable = False

and run in pdb, PyDev or PyCharm::

    mistral/cmd/launch.py --server all --config-file etc/mistral.conf --use-debugger

Running examples
----------------

To run the examples find them in mistral-extra repository (https://github.com/stackforge/mistral-extra) and follow the instructions on each example.
