#####################
 Modian Live-Wrapper
#####################

Modian-live-wrapper is a forn of `live-wrapper`_, originally developed
by the `Debian Live Team`_ which can be used to create Debian-based live
images for use with CDs, DVDs or USB sticks.

.. _`live-wrapper`: https://salsa.debian.org/live-team/live-wrapper
.. _`Debian Live Team`: https://www.debian.org/devel/debian-live/

It support customization of the generated image by running an ansible
script on the chroot, plus a pre-squashfs and pre-xorriso customization
hooks, to cover cases that are beyond Ansible's reach.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   quickstart
   commandline
   ansible
   chroot-fixups
   build-directories
   custom-kernels
   repositories
   customize-squashfs
