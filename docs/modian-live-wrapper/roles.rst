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

To use this you need to first build an iso of a modian system (e.g.  one
of the ``modian-full-example-*``), and point to it in the variable
``legacy_guest_iso`` in ``ansible/extra_vars.yaml`` of your project (the
path must be relative to the directory ``ansible``).
