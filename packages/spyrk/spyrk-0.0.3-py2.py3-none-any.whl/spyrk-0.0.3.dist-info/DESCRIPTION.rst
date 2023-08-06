Spyrk
=====

Python module for Spark devices.

Use it as follow:

..  code:: python

    from spyrk import SparkCloud

    USERNAME = 'he.ho@example.com'
    PASSWORD = 'pasSs'
    ACCESS_TOKEN = '12adza445452d4za524524524d5z2a4'

    spark = SparkCloud(USERNAME, PASSWORD)
    # Or
    spark = SparkCloud(ACCESS_TOKEN)

    # List devices
    print spark.devices

    # Access device
    spark.devices['captain_hamster']
    # Or, shortcut form
    spark.captain_hamster

    # List functions and variables of a device
    print spark.captain_hamster.functions
    print spark.captain_hamster.variables

    # Tell if a device is connected
    print spark.captain_hamster.connected

    # Call a function
    spark.captain_hamster.digitalwrite('D7', 'HIGH')
    print spark.captain_hamster.analogread('A0')
    # (or any of your own custom function)

    # Get variable value
    spark.captain_hamster.myvariable

Currently supporting:
---------------------

* Initialisation by username/password (generating a new access token every time).
* Initialisation by access token (get it from the Build Web IDE).
* Automatic discovery of devices.
* Automatic discovery of functions and variables in a device.
* Calling a function.
* Accessing a variable value.

Not yet supported:
------------------

* Subscribing and publishing events
* Any PUT method of the API (like uploading a firmware or application.cpp). That would be cool though.

Installation
------------

..  code:: bash

    $ pip install spyrk

Licensing and contributions
---------------------------

Spyrk is licensed under LGPLv3 and welcome contributions following the `C4.1 - Collective Code Construction Contract <http://rfc.zeromq.org/spec:22>`_ process.


Individual Contributors
=======================

A list of people who have contributed to Spyrk in order of their first
contribution.

Format: ``Name-or-Well-known-alias <email@domain.tld> (url)``

* Axel Voitier <axel.voitier@gmail.com>
* Wojtek Siudzinski <admin@suda.pl>

Please, add yourself when you contribute!


CHANGELOG
=========

0.0.3 - ?
--------------------

- Fixed Python 3 support

0.0.2 - 30 July 2014
--------------------

- Complying to Flake8 code-style checker
- Added accessing variable value
- Added `requires_deep_update` to Device declaration
- Fixed logging in bug and updated to support `requires_deep_update` value for the device
- Added setup.py and refactored main package as Spyrk.SparkCloud

0.0.1 - 26 January 2014
-----------------------

- Initial dump of code


