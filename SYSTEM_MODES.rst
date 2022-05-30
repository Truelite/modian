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

