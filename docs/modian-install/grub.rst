********************
 Grub Configuration
********************

Grub on the *installed* system can be configured by setting the
following two variables in ``/etc/modian/config.sh``:

``SYSTEMD_TARGET``
   the default target to reach at the first boot, default is
   ``default.target``;
``INSTALLED_BOOT_APPEND``
   additional parameters to pass to the kernel commandline.

These values can be set via the ansible playbook that is used to
configure the installer image, and are read at installation time.
