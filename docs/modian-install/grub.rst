********************
 Grub Configuration
********************

Grub on the *installed* system can be configured by setting the
following two variables in one of the files read by the
:doc:`configuration`:

``systemd_target``
   the default target to reach at the first boot, default is
   ``default.target``: note that this should be set in a ``.yaml`` file
   rather than ``config.sh``, so that the ``update_grub_system_modes``
   script has easier access to i;
``installed_boot_append``
   additional parameters to pass to the kernel commandline.

These values can be set via the ansible playbook that is used to
configure the installer image, and are read at installation time.
