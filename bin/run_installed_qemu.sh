#!/bin/sh

# Run the installed image live_test.qcow2 inside qemu.

# stop on error
set -e

# adding parameter
if [ "$#" != "" ]; then
    QEMU_MEM=$1
else
    QEMU_MEM=1G
fi

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
    -hda live_test.qcow2
