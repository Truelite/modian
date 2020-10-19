*******************************
 Extra squashfs customizations
*******************************

You can use ``--customize-squashfs`` to run a command (usually a
shellscript) just before ``mksquashfs`` is run, and after the
:doc:`chroot-fixups` are run.

The command will be passed the absolute path of the chroot as the only
argument.

You probably will not need to use this feature, but it can be useful to
implement custom functionality that would be hard to do otherwise.

As an example, this customization script implements allowing the
packages you install in the chroot to install customization hooks::

   #!/bin/sh

   # $1 is the path to the chroot root

   set -ue

   chroot $1 run-parts -v /usr/share/my-system/chroot-hooks
   rm -rf /usr/share/my-system/chroot-hooks
