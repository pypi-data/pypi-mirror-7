**********
Mopidy-NAD
**********

.. image:: https://img.shields.io/pypi/v/Mopidy-NAD.svg?style=flat
    :target: https://pypi.python.org/pypi/Mopidy-NAD/
    :alt: Latest PyPI version

.. image:: https://img.shields.io/pypi/dm/Mopidy-NAD.svg?style=flat
    :target: https://pypi.python.org/pypi/Mopidy-NAD/
    :alt: Number of PyPI downloads

.. image:: https://img.shields.io/travis/mopidy/mopidy-nad/master.png?style=flat
    :target: https://travis-ci.org/mopidy/mopidy-nad
    :alt: Travis CI build status

.. image:: https://img.shields.io/coveralls/mopidy/mopidy-nad/master.svg?style=flat
   :target: https://coveralls.io/r/mopidy/mopidy-nad?branch=master
   :alt: Test coverage

`Mopidy <http://www.mopidy.com/>`_ extension for controlling volume using an
external NAD amplifier. Developed and tested with a NAD C355BEE.


Installation
============

Install by running::

    sudo pip install Mopidy-NAD

Or, if available, install the Debian/Ubuntu package from `apt.mopidy.com
<http://apt.mopidy.com/>`_.


Configuration
=============

The Mopidy-NAD extension is enabled by default. To disable it, add the
following to ``mopidy.conf``::

    [nad]
    enabled = false

The NAD amplifier must be connected to the machine running Mopidy using a
serial cable.

To use the NAD amplifier ot control volume, set the ``audio/mixer`` config
value in ``mopidy.conf`` to ``nad``. You probably also needs to add some
properties to the ``nad`` config section.

Supported properties includes:

- ``port``: The serial device to use, defaults to ``/dev/ttyUSB0``. This must
  be set correctly for the mixer to work.

- ``source``: The source that should be selected on the amplifier, like
  ``aux``, ``disc``, ``tape``, ``tuner``, etc. Leave unset if you don't want
  the mixer to change it for you.

- ``speakers-a``: Set to ``on`` or ``off`` (or ``true`` or ``false``) if you
  want the mixer to make sure that speaker set A is turned on or off. Leave
  unset if you don't want the mixer to change it for you.

- ``speakers-b``: See ``speakers-a``.

Configuration example with minimum configuration, if the amplifier is available
at ``/dev/ttyUSB0``::

    [audio]
    mixer = nad

Configuration example with minimum configuration, if the amplifier is available
elsewhere::

    [audio]
    mixer = nad

    [nad]
    port = /dev/ttyUSB3

Configuration example with full configuration::

    [audio]
    mixer = nad

    [nad]
    port = /dev/ttyUSB0
    source = aux
    speakers-a = true
    speakers-b = false


Project resources
=================

- `Source code <https://github.com/mopidy/mopidy-nad>`_
- `Issue tracker <https://github.com/mopidy/mopidy-nad/issues>`_
- `Download development snapshot <https://github.com/mopidy/mopidy-nad/tarball/master#egg=Mopidy-NAD-dev>`_


Changelog
=========

v2.0.0 (2014-07-21)
-------------------

- Require Mopidy >= 0.19 and the new Mopidy mixer API.

- The configuration format has changed, due to the move from GStreamer 0.10's
  mixer API to Mopidy's new mixer API.

v1.1.0 (2014-01-20)
-------------------

- Require Mopidy >= 0.18.

v1.0.0 (2013-10-08)
-------------------

- Update to match the ``cookiecutter-mopidy-ext`` project template.

v0.3 (2013-04-16)
-----------------

- Include ``README.rst`` and ``LICENSE`` in PyPI package.

v0.2 (2013-04-16)
-----------------

- Add missing ``create_track()`` helper function.

v0.1 (2013-04-16)
-----------------

- Extracted extension from Mopidy core.


