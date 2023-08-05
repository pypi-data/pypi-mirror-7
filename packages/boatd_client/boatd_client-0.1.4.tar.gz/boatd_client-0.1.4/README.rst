============
python-boatd
============

.. image:: https://pypip.in/v/boatd_client/badge.png
    :target: https://pypi.python.org/pypi/boatd_client
    :alt: Latest PyPI version

.. image:: https://travis-ci.org/boatd/python-boatd.png?branch=master
    :target: https://travis-ci.org/boatd/python-boatd

Python module for writing `boatd <https://github.com/boatd/boatd>`_ behavior
scripts.

Installing
==========

``pip install boatd_client``

class **Boat**
==============

A boat controlled by boatd


**Attributes**
----------------

``heading``:
Return the current heading of the boat in degrees

``position``:
Return a tuple in the form ``(latitude, longitude)``

``version``:
Return the version of boatd

``wind``:
Return the direction of the wind in degrees

**methods**
-----------

``def __init__(self, host='localhost', port=2222)``

Create a boat instance, connecting to boatd at ``host`` on port ``port``

``def __rudder__(self, angle)``

Set the angle of the rudder to be ``angle`` degrees

``def __sail__(self, angle)``

Set the angle of the sail to ``angle`` degrees

