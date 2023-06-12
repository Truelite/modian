#!/bin/sh

set -ue

VMLINUX=$(ls $1/live/vmlinuz-*|sort -V|tail -n1)
INITRD=$(ls $1/live/initrd.img-*|sort -V|tail -n1)
cp $VMLINUX $1/live/vmlinuz
cp $INITRD $1/live/initrd.img
(cd $1 && md5sum ./live/* > md5sum.txt)
