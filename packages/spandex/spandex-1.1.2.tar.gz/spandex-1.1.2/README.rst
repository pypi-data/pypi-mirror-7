=======
Spandex
=======

Execute `elastic-recheck <https://github.com/openstack-infra/elastic-recheck>`_
query files and analyze the results - all in a CLI.

Usage
-----

.. code:: bash

    $ spandex openstack/elastic-recheck/queries/1331274.yaml
    total hits: 133
    build_status
      100% FAILURE
    build_name
      48% check-grenade-dsvm
      15% check-grenade-dsvm-partial-ncpu
      13% gate-grenade-dsvm
      9% check-grenade-dsvm-icehouse
      9% check-grenade-dsvm-partial-ncpu-icehouse
    build_branch
      95% master
      4% stable/icehouse
