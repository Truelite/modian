=======================
 modian-legacy-example
=======================

This is an example of a system that runs a legacy modian image inside
qemu.

To build this you need to first build an iso of a modian system (e.g.
one of the modian-full-example-*), and point to it in the variable
``legacy_guest_iso`` in ``ansible/extra_vars.yaml`` (the path must be
relative to the directory ``ansible``).

The legacy iso will be included in the generated iso.

To run the installed host system under qemu with the
``../bin/run_installed_qemu.sh`` script you should set the environment
variable ``QEMU_MEM=4G`` to have enough ram in the virtualized host to
run the guest.
