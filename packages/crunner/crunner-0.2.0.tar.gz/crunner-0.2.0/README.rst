crunner
=======
crunner is small application to run test after every change and notify about results.

Main features:

* continuously watch directories
* execute proper tests after every change
* send notification about test result
* test framework independent
* notifier independent

Requirements
============

* Python 2.7.x (not tested with Python 3.x)
* watchdog     (python package)
* mock         (for testing)

Continues Integration
=====================
.. image:: https://drone.io/github.com/pchomik/crunner/status.png
     :target: https://drone.io/github.com/pchomik/crunner/latest

Download
========
Latest version of plugin is available in `drone.io project artifacts <https://drone.io/github.com/pchomik/crunner/files>`_.

Install
=======
pip install crunner

Configuration
=============
Configuration file **.crunner.json** has to created in user home directory. The format of the file looks like below:

::

    {
      "notifier": {
        "cmd": "/usr/bin/notify-send",
        "img_arg": "-i",
        "msg_arg": "",
        "add_args": ""
      },
      "tester": {
        "cmd": "/usr/local/bin/py.test",
        "args": "-s --timeout 1 --random --pep8",
        "run_on_startup": true
      },
      "projects": {
        "crunner": {
          "active": true,
          "test_path": "/home/user/workspace/crunner/test/",
          "project_path": "/home/user/workspace/crunner"
        }
      }
    }

Presented configuration is notifier and test framework independent. It is possible to extend this configuration to watch
multiple projects by adding new configuration project.

Contribution
============
Please feel free to present your idea by code example (pull request) or reported issues.

License
=======
crunner - Application to run test continuously and notify about every change

Copyright (C) 2014 Pawel Chomicki

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.


