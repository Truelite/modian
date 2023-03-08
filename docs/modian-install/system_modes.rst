**********************************
 System mode selection for modian
**********************************

Modian supports configuring systems to behave in different ways depending on
the ``systemd.unit=`` set in the kernel commandline.

This is done by generating a set of systemd ``.target`` files both for system
and for user sessions, and an ``Xsession`` glue to activate the right target in
users' sessions based on the system target configured in the kernel command
line.

This is configured by adding to Ansible's extra vars a list with system mode
descriptions::

    modian_system_modes:
     - name: kiosk
       description: Locked down kiosk mode
       documentation: https://docs.example.org/system-modes/kiosk
     - name: maint
       description: Maintenance mode
       documentation: https://docs.example.org/system-modes/maint

Only the ``name`` key is mandatory. The other keys are optional and, if
present, will be added to the relevant ``.target`` files.

Customizing behaviour based on system modes
===========================================

For each system mode, a target ``modian-mode-$NAME.target`` is created both in
the system and in the user systemd sessions, so that different behaviour can be
easily implemented by adding units that depend on the right
``modian-mode-$NAME.target``.

For example, this file as ``~user/.config/systemd/user/xeyes.service`` will
start xeyes when the system starts as ``modian-mode-kiosk.target``::

        [Unit]
        Description=Automatic start xeyes
        PartOf=graphical-session.target

        [Service]
        Type=idle
        ExecStart=/usr/bin/xeyes
        RestartSec=3s
        Restart=always

        [Install]
        WantedBy=modian-mode-kiosk.target

The file will need to be activated with ``systemctl --user enable
xeyes.service``, or by manually creating the equivalent symlink.

System services can similarly be ``WantedBy=modian-mode-….target`` and
they can be enabled via ansible with::

   - name: enable <name> in kiosk mode
     systemd:
       name: <name>.service
       enabled: true
       masked: no

Grub Configuration
==================

To make it easier to change the system mode for the next boot, the grub
configuration installed by modian adds ``systemd.unit=$start_unit`` to
the kernel command line, and sets the variable ``start_unit`` earlier to
the value :doc:`configured <configuration>` as ``systemd_target``.

The script ``/usr/sbin/update_grub_system_modes`` reads the value of
``systemd_target`` from the modian configuration and updates the
variable ``systemd.unit`` in the grub configuration.

Note that the script reads the same ``.yaml`` files as
``modian-install`` and the environment, but it **doesn't** source
``/etc/modian/config.sh``: to read configuration from it you will have
to source it yourself in the shell that runs
``update_grub_system_modes``.
The recommended solution is to read the grub configuration from a
``.yaml`` file however, since ``config.sh`` is mostly there for legacy
reasons.

See also :doc:`grub`.

Troubleshooting
===============

To verify whether everything is correctly configured, on a running
modian system:

* the grub configuration in ``/live/image/boot/grub/grub.cfg`` must
  include the line ``set start_unit=modian-mode-<name>.target`` and the
  kernel commandline must include ``systemd.unit=$start_unit``;
* the same should appear in ``/proc/cmdline``
  ``modian-mode-<name>.target`` ;
* ``modian-mode-<name>.target`` should appear in the output of the
  command ``systemctl status "*.target"``;
* ``modian-mode-<name>.target`` should appear in the output of the
  command ``systemctl --user status "*.target"`` run as the regular
  user.
