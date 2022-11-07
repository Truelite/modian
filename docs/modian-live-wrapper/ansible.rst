***************
 Ansible usage
***************

After creating a chroot system with debootstrap, modian-live-wrapper
uses ansible to customize it.

You can choose the playbook using the ``--playbook`` option, which
defaults to ``chroot.yaml``, and a file of extra variables with the
option ``--ansible-extra-vars``, defaulting to ``extra_vars.yaml``.

modian-live-wrapper passes some extra variables to ansible playbook,
that you can use in your templates:

``distribution``:
   value of the ``--distribution`` command line option
``architecture``:
   value of the ``--architecture`` command line option
``build_mirror``:
   value of the ``--mirror`` command line option
``installed_mirror``
   value of the ``--apt-mirror`` command line option
``playbook``:
   value of the ``--playbook`` command line option
``kernel_package``:
   name of the kernel image package for the current architecture (see
   :doc:`custom-kernels`)

modian-live-wrapper provides a ``live`` role in
``roles/live/tasks/main.yaml`` that sets up a live system: you can add
it to the roles in your custom playbook by using a relative path, e.g.::

   roles:
     - example
     - ../modian-live-wrapper/roles/live

other roles, like ``example`` above are searched in the directory
``roles`` where the playbook lives.

Here are some example rules you can use in a custom playbook::

    - name: set live system hostname
      hostname:
        name: example

    - name: install extra packages
      apt:
        name: mc,moreutils,num-utils
        state: present

You can enable an internal repository, with its signing key. If the
value of ``filename`` starts with ‘inst-’, it will be considered a
repository used only at live build time and removed before generating
the squashfs image.

Note that the repository key will not be automatically removed. Please
file an issue (possibly a merge request) if you need it to happen. ::

    - name: add internal repository key
      copy:
        src: <filename>-keyring.gpg
        dest: /usr/share/keyrings/internal-keyring.gpg
    - name: enable internal repository
      apt_repository:
        repo: deb [signed-by=/usr/share/keyrings/<filename>-keyring.gpg] http://example.local/debian bookworm main
        filename: our-internal-repository
        state: present

where ``internal.keyring.gpg`` is the *dearmoured* key you want to use
and is available to ansible in an appropriate ``files`` directory.
