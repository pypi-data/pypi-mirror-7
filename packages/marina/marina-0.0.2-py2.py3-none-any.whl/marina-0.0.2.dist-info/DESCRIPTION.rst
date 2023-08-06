marina
======

Marina is a tool for building docker images with a focus on separating
compile-time dependencies from run-time dependencies in order to keep
the shipped images small and secure.

Usage
-----

::

  marina -vvv build examples/shootout

App Config
----------

::

  name: dummy

  compile:
    base_image: ubuntu:14.04
    commands:
      - dd if=/dev/urandom of=/srv/dummy bs=50kB count=1
    files:
      - /srv/dummy

  run:
    base_image: ubuntu:14.04


0.0.2 (2014-07-12)
==================

- Support ``--quiet`` for suppressing output.

- [build] Add ``--env`` option for specifying credentials and other
  configurable build-time settings.

- [build] Ensure the ``busybox`` image is around.

0.0.1 (2014-07-03)
==================

- Initial release.

- First cut at "marina build" to generate a working docker container.


