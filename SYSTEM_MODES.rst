System mode selection for modian
================================

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
-------------------------------------------

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

System services can similarly be ``WantedBy=modian-mode-….target``.

