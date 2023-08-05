##############################################
 overwatch - Python Logging Overwatch
##############################################

:Version: 1.3.2

Introduction
------------

`overwatch` is easily integrable two-in-one package built to simplify local
dev & debug processes. This package contains both client and server with GUI.
It includes special logger and GUI written in GTK2 that allows you
to perform real-time logs monitoring from a bunch of applications.

You need PyGTK 2.0 installed in order to run this properly.

App idea inspired by `loggly` service which is great but not free.

Installation
============

You can install ``overwatch`` either via the Python Package Index (PyPI)
or from source.

To install using ``pip``,::

    $ pip install overwatch


To install using ``easy_install``,::

    $ easy_install overwatch


Usage
===========

Integrating into script
-----------------------

You should simply add these lines within the head of your Python application:::

    import overwatch
    overwatch.init('My app friendly name')

Server handles all clients independantly, so you can patch as many scripts as you want.
All their logs will be captured in parallel.


Browsing logs
-----------------------------------

Just execute this command on the same machine:::

    $ python2 -m overwatch

Enjoy!

Contributing
============

Development of ``overwatch`` resides at: http://bitbucket.org/AndrewDunai/overwatch

You are highly encouraged to participate in the development.

License
=======

This software is licensed under the ``GNU GPL v2``.

