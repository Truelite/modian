*******************
 Managing projects
*******************

The recommended way to manage a modian-lwr project is as a script that
calls ``modian-lwr`` with the desired options, stored in revision
control together with the ansible playbook and other customization
scripts that are required.

A pretty minimal example is available in this repository as
``modian-live-example`` and is described in this document.

Directory structure
===================

The most important part of the project is of course the build script,
called e.g. ``build_<project_name>``, whose contents are documented
`below <build_script>`_.

The other directories will include everything that is needed to
customize the image:

``ansible``:
   contains a playbook (e.g. ``ansible/chroot.yaml``) which is applied
   to the generated chroot used to create the image and a ``roles``
   subdirectory with the ansible roles it uses, see :doc:`ansible` for
   more details;
``customize``:
   can contain scripts used for :doc:`customize-squashfs` (e.g.
   ``customize/squashfs.sh`` and for :doc:`customize-iso` (e.g.
   ``customize/iso.sh``.

You may want to configure your revision control to ignore the
directories ``build``, ``cache`` and ``dest``, as those are generated
when building the image and should not be stored.

.. note::

   Most of the file names in this section are just suggestion and can be
   changed by setting the appropriate options in the build scripts.

Build script
============



Next Steps
==========

To learn more about using live-wrapper, you can read the
:doc:`commandline` or browse through the rest of the documentation.
