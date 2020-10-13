# Post-ansible fixups

After ansible is run, and before the chroot is packed with mksquashfs,
live-wrapper performs a few final fixups, that are listed here.

For further customization of the squashfs, see [Extra squashfs
customizations](doc/customize-squashfs.md).

## `update-initramfs`

`update-initramfs` is run inside the chroot, to regenerate the initramfs to
include contents from packages that may have been installed via ansible.

## Finalize the apt mirror

At this stage, live-wrapper removes the mirrors used only at build time, and
sets up the mirrors that will be used in the final live image:

* `/etc/apt/sources.list` is removed
* `/etc/apt/sources.list.d/inst-*` files are removed
* `/etc/apt/sources.list.d/base.list` is added with the contents from
  `--apt-mirror` and `--apt-mirror-components`
* `apt-get update` is run, but a failure is tolerated (in case you do not have
  access to the final mirrors at build time)
* `apt-get clean` is run to remove packages cached at build time

Any repositories left in `/etc/apt/sources.list.d/` in files that do not begin
with `inst-*` are intentionally preserved, so you can use ansible to set up
final mirrors as well. See [Package Repositories](repositories.md) and [Ansible
usage](ansible.md).


## Enabling networkd (if `--networkd` is used)

If you use `--networkd`, the base image will be setup for networkd usage:

* `systemd-networkd` and `systemd-resolved` will be enabled
* `/etc/resolv.conf` will be replaced with a symlink to
  `/run/systemd/resolve/resolv.conf`
