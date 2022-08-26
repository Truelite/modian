*******
 Utils
*******

Running the generated images in qemu
====================================

There are two scripts to help testing generated images in qemu.

``bin/run_iso_qemu.sh``
   runs the iso inside qemu, changing its boot options to print on
   serial so that qemu can redirect it to the console, for ease of
   debugging.

   A disk image ``live_test.qcow2`` is generated in case it does not
   already exist.

   By default runs the first image that matches ``dest/modian*iso``, or
   any image passed as the first parameter on the command line.

``bin/run_installed_qemu.sh``
   runs the disk image ``live_test.qcow2`` inside qemu, with the regular
   graphical output.


.. _local_repo:

``local-repo``
==============

``local-repo`` is a tool to create and manage a simple local apt
repository suitable to provide copies of locally modified packages to
``modian-live-wrapper``.

Installation
------------

``local-repo`` can be run in-place and its dependencies are just
``reprepro`` and the Python 3 standard library.

Usage
-----

To create an apt repository in the directory ``repo``::

   ./local-repo.py create

To add a package to the repository::

   ./local-repo.py add-deb path/to/package.deb

To serve the apt repository on port 8099::

   ./local-repo.py serve
