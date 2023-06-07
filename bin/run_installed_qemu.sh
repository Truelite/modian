#!/bin/sh

# Run the installed image live_test.qcow2 inside qemu.

# stop on error
set -e

# memory allocated to qemu
QEMU_MEM=${QEMU_MEM:-"2G"}

# To add custom kernel parameters we should pass a kernel to qemu and add
# -append "boot=live ip=frommedia persistence-path=/live-0.1/ persistence
# live-media-path=live-0.1 consoleblank=0 console=ttyS0 printk.devkmsg=on" to
# keep the script generic, you can press [tab] at the bootloader menu and
# simply add the following options manually: console=ttyS0 printk.devkmsg=on
echo "running qemu"
qemu-system-x86_64 \
    -m $QEMU_MEM \
    -serial stdio \
    -vga cirrus \
    -cpu host \
    -enable-kvm \
    -hda live_test.qcow2
