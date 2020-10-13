# Custom kernels

By default, `live-wrapper` installs during the initial `debootstrap` step the
default kernel package for the distribution it is building.

If you want to install a different kernel, you can use the `--no-auto-kernel`
option to stop `live-wrapper` from installing a kernel by default, and then
install a kernel of your choosing using the ansible playbooks.

`live-wrapper` will set an ansible variable called `kernel_package` to contain
the name of the Linux kernel image for the current distribution and
architecture (for example, `linux-image-amd64`, `linux-image-armmp`, and so
on).

For example, this playbook snippet will build a live image using the kernel
from `stretch-backports`:

```
   - name: enable backports repository
     apt_repository:
       repo: deb http://ftp.it.debian.org/debian/ stretch-backports main
       filename: inst-backports
       state: present
   - name: install kernel from backports
     apt:
       name: "{{kernel_package}}"
       state: present
       default_release: stretch-backports
       update_cache: yes
```

Note that all apt source configuration files that begin with `inst-` will be
used only to build the distribution, and will be removed before the squashfs
image is built.

You can pick a specific kernel version using normal [ansible
apt](https://docs.ansible.com/ansible/latest/modules/apt_module.html)
functionality:

```
   - name: install a specific kernel version
     apt:
       name: "{{kernel_package}}>=4.19"
       state: present
       default_release: stretch-backports
       update_cache: yes
```

Or you can choose an arbitrary custom built kernel image from a custom
repository if you need it:

```
   - name: enable custom repository
     apt_repository:
       repo: deb http://example.com/debian/ example main
       filename: inst-example
       state: present
   - name: install custom kernel image
     apt:
       name: "linux-image-example=4.19"
       state: present
       default_release: example
       update_cache: yes
```
