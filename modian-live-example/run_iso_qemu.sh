#!/bin/sh
  
# Run an iso inside qemu

# stop on error
set -e

ISO=${1:-"dest/modian-example.iso"}

# To add custom kernel parameters we should pass a kernel to qemu and add 
# -append "boot=live components debug timezone=Europe/Rome ip=frommedia consoleblank=0 console=ttyS0 printk.devkmsg=on"
# to keep the script generic, you can press [tab] at the bootloader menu and
# simply add the following options manually:
# console=ttyS0 printk.devkmsg=on
qemu-system-x86_64 \
    -m 1G \
    -cdrom "$ISO" \
    -serial stdio \
    -boot d
