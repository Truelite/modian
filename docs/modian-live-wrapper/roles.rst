***************
 Ansible roles
***************

modian-live-wrapper includes a collection of ansible roles which can be
used in the ansible playbook to configure common usecases.

``live``
========

Sets up a live system, and it's probably always required.

``modian``
==========

Installs the modian packages, and is probably always required.

``modian-system-modes``
=======================

``legacy``
==========

Sets up a system that creates an host live image that includes another
live image and runs it inside qemu. 

To use this you first need to have an iso of a modian system (e.g. one
of the ``modian-full-example-*``) and to set the following two variables
in ``ansible/extra_vars.yaml``:

* ``legacy_guest_iso``, pointing to said iso;
* ``legacy_conf``, pointing to a yaml file with the configuration that
  will be used to run qemu inside the image.

The latter can have the following contents:

* ``iso``, default ``/srv/iso/guest.iso``;
* ``kernel``, default ``/srv/iso/guest.iso.kernel``;
* ``initrd``, default ``/srv/iso/guest.iso.initrd``;
* ``cmdline``, default ``boot=live config username=root
  hostname=controller persistent consoleblank=0 --``;
* ``hda``, ``hdb``, ``hdc``, ``hdd``, passed to the qemu options of the
  same name, to pass disks or disk images to the guest;
* ``nic``, a list of strings that will be passed as ``--nic`` options to
  qemu, to configure the network.
