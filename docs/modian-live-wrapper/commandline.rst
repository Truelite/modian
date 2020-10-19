************************
 Full command line help
************************

.. code:: text

   usage: modian-lwr  [-h] [--version] [--log-level LOG_LEVEL] [--log FILE]
                 [--distribution NAME] [--architecture ARCH]
                 [--apt-mirror mirror_url]
                 [--apt-mirror-components main [contrib [..]]]
                 [--playbook file.yaml] [--networkd]
                 [--tasks "task-TASK1 task-TASK2 ..."]
                 [--extra "PKG1 PKG2 ..."]
                 [--firmware "PKG1 PKG2 ..."]
                 [--customize-squashfs script.sh]
                 [--no-auto-kernel] [--image-output file.iso]
                 [--mirror mirror_url]
                 [--cache-dir path] [--work-dir path]
                 [--retry] [--volume-id VOLID]
                 [--description DESCRIPTION]
                 [--no-grub] [--grub-loopback-only] [--no-isolinux]
                 [--bootappend string] [--boot-timeout seconds]
                 [--no-installer]
                 [--di-daily] [--base-debs "PKG1 PKG2 ..."]
                 [--squashfs-comp gzip|lzo|gz]
                 [--customize-iso script.sh]

   Build a live Debian image

   optional arguments:
     -h, --help            show this help message and exit
     --version             show program's version number and exit
     --log-level LOG_LEVEL
                           log at LEVEL, one of debug, info, warning,
                           error, critical, fatal (default: debug)
     --log FILE
                           write log entries to FILE. Special values:
                           stderr, none (default: stderr)

   Distribution Settings:
     --distribution NAME, -d NAME
                           Debian release to use (default: stretch)
     --architecture ARCH   architecture to use (default: amd64)
     --apt-mirror mirror_url
                           Mirror to configure in the built image
                           (default: http://deb.debian.org/debian/)
     --apt-mirror-components main [contrib [..]]
                           Components to activate in the built image
                           apt configuration (default: main)
     --playbook file.yaml
                           Ansible playbook to run to customize the
                           system (default: chroot.yaml)
     --networkd
                           Enable systemd-networkd and
                           systemd-resolved (default: False)
     --tasks "task-TASK1 task-TASK2 ...", -t "task-TASK1 task-TASK2 ..."
                           Task packages to install (default: )
     --extra "PKG1 PKG2 ...", -e "PKG1 PKG2 ..."
                           Extra packages to install (default: )
     --firmware "PKG1 PKG2 ...", -f "PKG1 PKG2 ..."
                           Firmware packages to install (default: )
     --customize-squashfs script.sh
                           If set, run this script with the chroot path
                           as argument before running mksquashfs
                           (default: None)
     --no-auto-kernel
                           Do not automatically install a kernel in the
                           chroot.  When using this option, it is
                           assumed that the ansible playbook takes care
                           of installing a kernel (default: False)

   Base Settings:
     --image-output file.iso, -o file.iso
                           Location for built image (default: live.iso)
     --mirror mirror_url, -m mirror_url
                           Mirror to use for image creation (default:
                           http://deb.debian.org/debian/)
     --cache-dir path
                           If set, cache intermediate data in this
                           directory (default: None)
     --work-dir path
                           If set, work in this directory instead of a
                           temporary directory (default: None)
     --retry
                           Keep the existing work dir, and skip steps
                           for which output already exists (default:
                           False)

   ISO Settings:
     --volume-id VOLID
                           Volume ID for the image
                           (default: DEBIAN LIVE)
     --description DESCRIPTION
                           Description for the image to be created. A
                           description will be automatically generated
                           based on the distribution chosen if none is
                           specified. (default: Unofficial Debian
                           GNU/Linux 'dist' Live)
     --no-grub
                           Do not add GRUB bootloader to the image (for
                           EFI support) (default: True)
     --grub-loopback-only
                           Only install the loopback.cfg GRUB
                           configuration (for loopback support)
                           (overrides --grub) (default: False)
     --no-isolinux
                           Do not add isolinux bootloader to the image
                           (default: True)
     --bootappend string
                           Append this string to the kernel command
                           line (default: None)
     --boot-timeout seconds
                           Boot timeout in seconds (default: None)
     --no-installer
                           Include Debian Installer in the Live image
                           (default: True)
     --di-daily
                           Use the daily Debian Installer builds not
                           releases (default: False)
     --base-debs "PKG1 PKG2 ..."
                           Base packages for the installer (default: )
     --squashfs-comp gzip|lzo|gz
                           Squashfs compression algorithm
                           (default: lzo)
     --customize-iso script.sh
                           If set, run this script with the path to the
                           iso contents as argument before running
                           xorriso (default: None)
