********************
 Version Management
********************

``modian-install`` installs the system in a directory marked with a
version identifier, and there is support to switch between multiple
versions.

Installation
============

First installation
------------------

The first installation of modian is done through the live installer; it
will completely wipe the system, create and format its partitions and
install itself as the first live image available.

This happens if the installer doesn't detect an existing modian install
on the computer, or always if the iso label is ``firstinstall``;
otherwise a recovery installation is attempted.

Recovery installation
---------------------

When the live installer detects an existing modian install on a
computer, it will try to recover it.

* The partitions are checked for consistency (and if at least one of
  them is missing, a full install is performed instead; having a backup
  of any data that should be preserved is recommended).

* The root, log and esp partitions are formatted, everything else (user
  data) is preserved.

* The current live image is installed.

Updates
-------

Updates to a new version are done by:

* downloading the iso on the computer or connecting a usb key where the
  iso has been flashed;

* running the command::

     modian-install-iso <version name> --isoimage=<file or device>

  ``<version name>`` is what appears in the grub label and in the
  directory name and should be the same as used inside the image, but
  this isn't mandatory.

When updating, the latest 3 versions are kept, while older ones and
unsuccesful installations are purged.

Switching between versions is done at the grub menu.

Persistence file
================

Each version of the live system has its own persistence file: it is
stored in the directory ``live-<version>`` together with the live iso,
and after it has been created and initialized a gzipped copy is saved,
so that a factory reset only requires the command::

   zcat persistence.gz > persistence
