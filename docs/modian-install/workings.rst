**********
 Workings
**********

``modian-install`` is the :index:`installer` that runs on a modian
system, turning it from a generic live into a system with monolitic
updates.

It can be safely installed on any Debian system and provides an unit
``modian-install.install`` that runs the command ``modian-install
install`` which is actually runs the installation. The live image runs
this command thanks to the option
``"systemd.unit=modian-install.target"`` added to ``--bootappend`` in
the image generation script.

Partitions
==========

The following partitions are created and used by the installer:

root (filesystem label ``##root##``)
   with the bootloader, kernel, initrd, live images and two persistence
   files for each live image, an active one and a gzipped factory-reset
   one;
log (filesystem label ``##log##``)
   to keep shared logs;

plus two user partitions: data (filesystem label ``##data##``) and
images (filesystem label ``##images##``) whose names will be made
configurable in the future.

The idea is that user configuration and data, plus logs, are in the
additional partitions and shared between different live image versions,
while the persistence files only have system changes.

``modian-install-detect``
=========================

``modian-install-detect`` provides the shell functions called by the
installer to detect the existing partitions, working in two different
ways:

* first install, which wipes any existing partition;
* regular, which tries to recover an existing installation and update
  it.

When the ISO image volume id is ``firstinstall``, the first method is
selected, otherwise the second one is used. The script
``modian-install/changevolid`` can be used to change this value in an
existing iso, with no need to regenerate it.

The relevant selection code is in the method ``System.compute_actions``.

Feedback
========

Ad the end of the installation, the function ``do_feedback()`` from
``usr/share/modian-install/common.sh`` will print a red or green text
screen and sound a different beep to announce a failure or that the
installation has been completed.
