#!/bin/sh
  
# Run an iso inside qemu, changing its boot options to print on serial so that
# qemu can redirect it to the console, for ease of debugging.

# A disk image live_test.qcow2 is generated in case it does not already exist.

# stop on error
set -e

ISO=${1:-"dest/modian-full-example.iso"}

if [ ! -e live_test.qcow2 ] ; then
    qemu-img create -f qcow2 live_test.qcow2 40G
fi

bsdtar xf "$ISO" live/vmlinuz* live/initrd.img*

# To add custom kernel parameters we should pass a kernel to qemu and add 
# -append "boot=live components debug timezone=Europe/Rome ip=frommedia consoleblank=0 console=ttyS0 printk.devkmsg=on"
# to keep the script generic, you can press [tab] at the bootloader menu and
# simply add the following options manually:
# console=ttyS0 printk.devkmsg=on
qemu-system-x86_64 \
    -m 1G \
    -cdrom "$ISO" \
    -serial stdio \
    -boot d \
    -kernel live/vmlinuz* \
    -initrd live/initrd.img* \
    -append "boot=live components timezone=Europe/Rome ip=frommedia systemd.unit=modian-install.target consoleblank=0 console=ttyS0 printk.devkmsg=on" \
    -hda live_test.qcow2

