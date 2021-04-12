********************
 System Description
********************

Modian is a system to generate read-only Debian images with support for
monolithic updates and reverts.

It generates a bootable installer that runs from a bootable USB key and
installs or updates a system composed by a read-only image and a version
choice mechanism on the target machine.

It has the following components:

:doc:`modian-live-wrapper/index`:
   a simplified fork of live-wrapper to generate generic live images;
:doc:`modian-install/index`:
   ;
