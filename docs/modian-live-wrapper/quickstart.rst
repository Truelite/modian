************
 Quickstart
************

Super Fast Quickstart
=====================

Building images with live-wrapper is quite simple. For the impatient::

   # modian-lwr

This will build you a file named ``live.iso`` in the current directory
containing a minimal live-image.

Customising the Image
=====================

There are a number of supported command-line arguments that can be
passed to live-wrapper. These change the behaviour to create a
customised image.

Changing the Distribution
-------------------------

By default, the ISO image will be built using the ``trixie``
distribution. If you’d like to build using ``bookworm`` or ``sid`` you can
pass the ``-d`` parameter to live-wrapper like so::

   # modian-lwr -d bookworm

.. note::

   you must use the codename, and not the suite (e.g. stable),
   when specifying the distribution.

Using an Alternative Mirror
===========================

By default, live-wrapper will use the mirror configured in your
``/etc/apt/sources.list``. If you have a faster mirror available, you
may want to change the mirror you’re using to create the image. You can
do this with the ``-m`` parameter::

   # modian-lwr -m http://localhost/debian/

You may also configure the mirror that will be configured *inside* the
image. This will be used for any extra packages that are specified, and
will also be the mirror that the image will use after the build is
complete. Change this with the ``--apt-mirror`` parameter::

   # modian-lwr -m http://localhost/debian/ --apt-mirror http://deb.debian.org/debian

By default this is set to ``http://deb.debian.org/debian``.

Customising Packages
====================

There are several methods for specifying extra packages to be installed
into the live image:

``-t`` ``-–tasks``
   should be used to give a list of **task** packages to be included in
   the image. These will be installed while the initial ``debootstrap``
   run is made, so all their “Depends” and “Recommends” will be
   installed too, and they will be installed when the ansible playbook
   is run.

``-e`` ``--extra``
   allows for a list of extra non-task packages to be installed, also at
   ``debootstrap`` time with all their “Depends” and “Recommends”
   included.

``-f`` ``--firmware``
   allows for a list of firmware packages to be installed in the image,
   also at ``debootstrap`` time, with all their “Depends” and
   “Recommends” included.
   **Also** each of these packages
   will be downloaded and saved into the image so that an included
   installer will automatically find them for installation.

   .. warning::

      BEWARE that using the ``--firmware`` option is likely to mean your
      image will include non-free software. Check the licensing
      carefully before distributing it.

For example::

   # modian-lwr -e vim -t science-typesetting
   # modian-lwr -e "emacs25 jed" -t live-task-xfce -f "firmware-iwlwifi firmware-realtek"

Finally, if you want to make a live image that will work as a standalone
source for installation you will need to specify a list of “base”
packages. This is the list of packages that will need to be installed
*after* the contents of the live image is copied to the new system. This
is essentially a list of bootloader packages and a few utility packages
that they use. Specify this list with the ``--base_debs`` parameter. For
example, this is the list needed for Debian Stretch on amd64::

   # modian-lwr --base_debs "eject pciutils usbutils \
                keyboard-configuration console-setup \
                grub-efi-amd64 grub-efi-amd64-bin grub-pc"

Setting the Volume ID
=====================

The Volume ID is the embedded label in the ISO image; this is what will
be displayed on the desktop when a DVD or USB flash drive containing the
image is inserted into a computer. The default is ``DEBIAN LIVE``, or
you can change this using the ``--volume_id`` parameter. There is a
32-character limit for what can be specified here. Example:

::

   # modian-lwr --volume_id "My live image"

Testing the Image with QEMU
===========================

You can easily test your created live images with QEMU.

.. note::

   You will need to increase the amount of memory available to QEMU when
   running the live image. The image will crash if run with the default
   memory limit.

To test the image using BIOS boot::

   qemu-system-x86_64 -m 2G -cdrom live.iso

For EFI boot you will need to install the ``ovmf`` package and then
run::

   qemu-system-x86_64 -bios /usr/share/ovmf/OVMF.fd -m 2G -cdrom live.iso

To test with an emulated USB device, run::

   qemu-system-x86_64 -m 2G -usbdevice disk:live.iso

To test the speech synthesis installer option, you will need to add the
following to the QEMU invocation::

   -soundhw sb16,es1370,adlib

.. note::

   using ``-hda`` to attach the disk image will prevent the installer
   from detecting the “CD-ROM” as this is not a removable device, it is
   an emulated attached hard disk drive.

Next Steps
==========

To learn more about using live-wrapper, you can read the documentation
on :doc:`project` or browse through the rest of the documentation.
