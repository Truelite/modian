# live-wrapper

live-wrapper is a tool initially produced by the [Debian Live
Team](https://www.debian.org/devel/debian-live/) that can be used to create
Debian-based live images for use with CDs, DVDs or USB sticks.

Documentation index:

* [Quick start](doc/quickstart.md)
* [Command line usage](doc/commandline.md)
* [Ansible usage](doc/ansible.md)
* [Post-ansible fixups](doc/chroot-fixups.md)
* [Build directories](doc/build-directories.md)
* [Custom kernels](doc/custom-kernels.md)
* [Package repositories](doc/repositories.md)
* [Extra squashfs customizations](doc/customize-squashfs.md)
* [Extra iso customizations](doc/customize-iso.md)
* [Bootloader customization](doc/bootloader.md)
* [Development tips](doc/devel-tips.md)


## This is a forked version

This is Enrico's fork of
[live-wrapper](https://salsa.debian.org/live-team/live-wrapper)
with the following changes:


### Built-in chroot creation

Removed dependency on [vmdebootstrap](https://liw.fi/vmdebootstrap/).

I have integrated and reimplemented `vmdebootstrap`'s functionality in
`live-wrapper`, so it continues to work on `buster` after `vmdebootstrap` is
removed.


### Ported to python3

`live-wrapper` is now python3 only, and runs on Debian `buster`.


### Chroot customization via Ansible

I replaced the old `customize.sh` with an [Ansible](https://www.ansible.com/)
playbook, with the option of providing a custom playbook.

I added pre-squashfs and pre-xorriso customization hooks, to cover cases
that are beyond Ansible's reach.

I implemented built-in support for enabling systemd-networkd on the target
system.


### Performance improvements

I implemented caching of `debootstrap`'s result to be reused on subsequent runs
unless its arguments change.

I implemented caching of the contents of the chroot customized by ansible.

I use [eatmydata](https://www.flamingspork.com/projects/libeatmydata/) if
present, to try and speed up operations, since all chroots manipulated by
`live-wrapper` are ephemeral and only need to exist to be packed into a
squashfs.

I made the squashfs compression algorithm configurable, so that `lzo` can be
used for quicker development and `xz` for production runs.


### Inspectable
    
I implemented an option to leave the work directory on disk, so that
`live-wrapper`'s work can be inspected for debugging. `live-wrapper` also
writes scripts on the work directory that can be used to easily replicate
ansible and xorriso's invocations.
