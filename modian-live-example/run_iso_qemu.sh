#!/bin/sh
  
# Run an iso inside qemu, changing its boot options to print on serial so that
# qemu can redirect it to the console, for ease of debugging.

# stop on error
set -e

ISO=${1:-"dest/modian-example.iso"}

# If the kernel parameters aren't passed correctly, they can be added manually
# at the bootloader menu by pressing [tab]
qemu-system-x86_64 \
    -m 1G \
    -hdc "$ISO" \
    -serial stdio \
    -boot d
    -append "boot=live components debug timezone=Europe/Rome ip=frommedia consoleblank=0 console=ttyS0 printk.devkmsg=on"

