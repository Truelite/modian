************
 Quickstart
************

Setup
=====

To build a fully featured modian project like ``modian-full-example``
you need:

* an installation of modian-live-wrapper;
* a deb repository with the onther ``modian-*`` packages.

If you installed ``modian-live-wrapper`` from a repository you're
probably ok.

If you are working on modian itself and want to run a locally modified
version of the code, see :doc:`devel`.

Building
========

To build the iso for a modian project you need to run the building
script, e.g.::

   [sudo] ./build_example

this will generate an iso with the name specified in the script, e.g.
``dest/modian-full-example.iso``.

See :doc:`../modian-live-wrapper/project` for more details on the
building script and how it can be customized.
