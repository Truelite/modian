*******************
 Managing projects
*******************

The recommended way to manage a modian-lwr project is as a script that
calls ``modian-lwr`` with the desired options, stored in revision
control together with the ansible playbook and other customization
scripts that are required.

A pretty minimal example is available in this repository as
``modian-live-example`` and is described in this document.

A more complete example that includes modian features other than
modian-lwr is documented under :doc:`../modian-examples/index`.

Directory structure
===================

The most important part of the project is of course the build script,
called e.g. ``build_<project_name>``, whose contents are documented
`below <build_script>`_.

The other directories will include everything that is needed to
customize the image:

``ansible``:
   contains a playbook (e.g. ``ansible/chroot.yaml``) which is applied
   to the generated chroot used to create the image, a yaml file with
   additional ansible variables (e.g. ``ansible/extra_vars.yaml`` and a
   ``roles`` subdirectory with the ansible roles it uses, see
   :doc:`ansible` for more details;
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

.. _build_script:

Build script
============

The build script is where ``modian-lwr`` is run, and stores the
combination of options that is used for the specific project.

For some configuration keys, it is reasonable to expect that they may
have to be changed when building on a different machine: for those a
sensible default is provided, but they can be changed through one of the
following environment variable.

``MLW_DEST``
   the directory where the generated iso will be written.
``MLW_ISO``
   the name of the generated iso.
``MLW_MIRROR``
   the main debian mirror to use.
``MLW_ISO_VOLUME``
   volume ID of the generated iso.
``MLW_DESCRIPTION``
   description of the generated iso.
``MLW_EXTRA_VARS``
   a yaml file with extra variables, passed to ansible when configuring
   the chroot for the iso.
``FILELOG``
   the log file.
``MODIAN_LWR``
   the modian-lwr command; this can be used to run modian-lwr from the
   git checkout instead of an installed version by running the script
   as::

      [sudo] MODIAN_LWR=path/to/modian/modian-live-wrapper/lwr.py ./build_example

Next Steps
==========

To learn more about using live-wrapper, you can read the
:doc:`commandline` or browse through the rest of the documentation.
