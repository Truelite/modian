#!/bin/sh

set -ue

cp $1/live/vmlinuz-* $1/live/vmlinuz
cp $1/live/initrd.img-* $1/live/initrd.img
(cd $1 && md5sum ./live/* > md5sum.txt)
