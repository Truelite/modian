***********
 Slideshow
***********

Through this tutorial you will create an iso image that installs a
system that shows a slideshow of images and pdf files from a directory.

The system can then be updated (for a general system update, or to
change the way the slideshow works) by creating a new iso and running
it, and there is support to go back to the previous system in case the
update doesn't work as desired.

The installation / update iso is the same that will be installed in the
final system: a different systemd target will select whether to start
the installation scripts or the regular system.

Setup
=====

Files
=====

In your project directory, you will need to create the following
files and directories; you may copy the ones in
``modian-full-example-<distribution>`` and adapt them to your needs.

This section will explain their contents.

``ansible``
-----------

This directory contains the files that describe what will be in the
image.

``ansible/chroot.yaml``
-----------------------

This is the ansible playbook that will configure the contents of the iso.

Start the playbook and configure it to be run on all hosts (there will
be just one in the hosts list passed to ansible)::

   ---
   - hosts: all

Then you will need the roles provided by modian to setup the
installation / update system::

  roles:
      # live and modian roles from the common modian-live-wrapper roles
      - live
      - modian

Then we can add a role to configure our own usecase::

      - slideshow

Of course, simple configurations can be added directly as tasks to the
playbook; here we will setup two variables that are needed by modian::

   tasks:
     - name: set the modian release name
       lineinfile:
         path: /etc/modian/config.sh
         line: 'export MODIAN_RELEASE_NAME="0.1"'
         regexp: 'MODIAN_RELEASE_NAME="'
     - name: set the modian release full name
       lineinfile:
         path: /etc/modian/config.sh
         line: 'export MODIAN_RELEASE_FULL_NAME="0.1.0"'        
         regexp: 'MODIAN_RELEASE_FULL_NAME="'

``ansible/extra_vars.yaml``
---------------------------

This is a file with variables that will be passed to ansible; other than
what is used in your own roles you need to set a value for
``modian_repo`` to somewhere the modian packages can be installed from;
if using ``local_repo`` to serve them locally you can use::

   modian_repo: '[trusted=yes] http://localhost:8099/'

``ansible/roles``
-----------------

When run from modian, ansible will look for roles just in the modian
directories and in a directory called ``ansible/roles``; at the moment
there is no support to change it or add more directories, but symlinks
will work, if you need to share roles with other images.

``ansible/roles/slideshow/tasks/main.yaml``
-------------------------------------------

The tasks file in the ansible role that configures our slideshow-running
image: first we install the dependencies::

   ---
   - name: Install impressive 
     apt:
       name: impressive,ghostscript
       state: present

then we prepare the system to mount a filesystem with the label
``##slides##``::

   - name: "mountpoint for the ##slides## labeled filesystem"
     mount:
       path: /srv/slides
       src: "LABEL=##slides##"
       state: mounted
       fstype: auto
       opts: ro,noexec,nofail,x-systemd.device-timeout=10

impressive -g 800x600 -a 2 -w /srv/slides/

``customize/iso.sh``
--------------------

This bash script is run after the iso has been generated, and can be
used to do minor modifications; it must be executable, but it can be
empty, with just a working shebang::

   #!/bin/sh

If you want to run the image in qemu for tests, using the
``run_iso_qemu.sh`` script from mobian, you need to add the following
commands to add ``vmlinuz`` and ``initrd.img`` to the image (rather than
just the versioned files)::

   set -ue

   VMLINUX=$(ls $1/live/vmlinuz-*|sort -V|tail -n1)
   INITRD=$(ls $1/live/initrd.img-*|sort -V|tail -n1)
   cp $VMLINUX $1/live/vmlinuz
   cp $INITRD $1/live/initrd.img
   (cd $1 && md5sum ./live/* > md5sum.txt)

``customize/squashfs.sh``
-------------------------

This bash script is run after the iso has been generated, and can be
used to do minor modifications; it must be executable, but it can be
empty, with just a working shebang::

   #!/bin/sh

``build_image``
---------------

This scripts is used to run the ``modian-lwr`` command with all of its
parameters; for convienience they can be set through environment
variables in a way that makes them easy to override::

   #!/bin/bash

   MLW_DEST=${MLW_DEST:-dest}
   MLW_ISO=${MLW_ISO:-slideshow.iso}
   MLW_MIRROR=${MLW_MIRROR:-https://deb.debian.org/debian}
   MLW_ISO_VOLUME=${MLW_ISO_VOLUME:-slideshow}
   MLW_DESCRIPTION=${MLW_DESCRIPTION:-"Modian Full Example"}
   MLW_EXTRA_VARS=${MLW_EXTRA_VARS:-ansible/extra_vars.yaml}

   MODIAN_LWR=${MODIAN_LWR:-modian-lwr}

   FILELOG=${MLW_DEST}/slideshow-$(date "+%Y%m%d_%H%M%S").log

then some working directories are created::

   mkdir -p ${MLW_DEST}                                                            mkdir -p build/chroot

and finally modian-lwn is run::

   $MODIAN_LWR \
       --architecture=amd64 \
       -o ${MLW_DEST}/${MLW_ISO} \
       --distribution=bookworm \
       --mirror=${MLW_MIRROR} \
       --apt-mirror=${MLW_MIRROR} \
       --apt-mirror-components="main" \
       --volume-id="${MLW_ISO_VOLUME}" \
       --description="${MLW_DESCRIPTION}" \
       --playbook="ansible/chroot.yaml" \
       --ansible-extra-vars="${MLW_EXTRA_VARS}" \
       --bootappend="boot=live components timezone=Europe/Rome ip=frommedia systemd.unit=modian-install.target consoleblank=0" \                 
       --networkd \
       --boot-timeout=1 \
       --cache-dir=cache/ \
       --customize-squashfs="customize/squashfs.sh" \
       --customize-iso="customize/iso.sh" \
       --squashfs-comp="lzo" \
       --work-dir="build" \
       --no-installer  |& tee -a $FILELOG


Building
========

Exercises
=========

The program used to show the slideshow, impressive, is able to show
images 
