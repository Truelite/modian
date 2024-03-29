#!/bin/sh
  
# Run an iso inside qemu, changing its boot options to print on serial so that
# qemu can redirect it to the console, for ease of debugging.

# A disk image live_test.qcow2 is generated in case it does not already exist.

# stop on error
set -e

ISO=${1:-"$(ls dest/modian*iso | head -n 1)"}

if [ -z $ISO ] || [ ! -e $ISO ] ; then
    echo "No such file: $ISO"
    exit 1
fi

if [ ! -e live_test.qcow2 ] ; then
    qemu-img create -f qcow2 live_test.qcow2 40G
fi

if [ -x /usr/bin/bsdtar ]; then
    bsdtar xf "$ISO" live/vmlinuz live/initrd.img
else
    echo "bsdtar is not available; under debian it is in the package libarchive-tools"
fi

# memory allocated to qemu
QEMU_MEM=${QEMU_MEM:-"2G"}

# we run the iso as if it was an usb device, as cdroms are still not supported
# by modian-install
#
# by default qemu uses a legacy bios; adding the following option uses UEFI
# instead (requires the ovmf package to be installed):
#   -bios /usr/share/ovmf/OVMF.fd \

qemu-system-x86_64 \
    -m $QEMU_MEM \
    -hdc "$ISO" \
    -hda live_test.qcow2 \
    -enable-kvm \
    -serial stdio \
    -kernel live/vmlinuz \
    -initrd live/initrd.img \
    -append "boot=live components timezone=Europe/Rome ip=frommedia systemd.unit=modian-install.target consoleblank=0 console=ttyS0 printk.devkmsg=on" \
    -boot d
