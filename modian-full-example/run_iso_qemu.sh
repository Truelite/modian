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

if [ -x /usr/bin/bsdtar ]; then
    bsdtar xf "$ISO" live/vmlinuz* live/initrd.img*
else
    echo "bsdtar is not available; under debian it is in the package libarchive-tools"
fi

# we run the iso as if it was an usb device, as cdroms are still not supported
# by modian-install
qemu-system-x86_64 \
    -m 1G \
    -hdc "$ISO" \
    -serial stdio \
    -hda live_test.qcow2 \
    -kernel live/vmlinuz* \
    -initrd live/initrd.img* \
    -append "boot=live components timezone=Europe/Rome ip=frommedia systemd.unit=modian-install.target consoleblank=0 console=ttyS0 printk.devkmsg=on" \
    -boot d
