# SETUP_DEVICE      
# VERBOSE           'yes' to enable verbose output
# GRUB_LINUX_ARGS   (optional) arguments to pass to grub's linux image
# GRUB_INITRD_ARGS  (optional) arguments to pass to grub's initrd image
#
# do_partitions     Function that partitions target devices and creates file
#                   systems
# do_feedback       (optional) by default it gives feedback with beeps; redefine
#                   to get a different feedback
# do_install_target (optional) install this system on the target device. It has
#                   one parameter which is the directory where the target
#                   device is mounted. By default, it installs the
#                   multiple-squashfs scenario
#
# PERSISTENZA
# PERSIST_SIZE      Size of persistence data file (default: 2GiB)
# PERSIST_FILE      Nome del file di persistenza

GRUBCFG=/mnt/boot/grub/grub.cfg
# Set the following two variables to a sensible value in the ansible script
# that generates the target chroot.
MODIAN_RELEASE_NAME="<modian_release_name>"
MODIAN_RELEASE_FULL_NAME='<modian_release_full_name>'
HOSTNAME=$(hostname)
DIR_BOOTSCRIPT=/etc/modian/boot.d
INSTALLED_BOOT_APPEND=""
