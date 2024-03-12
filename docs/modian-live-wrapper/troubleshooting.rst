***************
Troubleshooting
***************

Troubleshooting boot-time issues
--------------------------------

When dealing with issues that happen at boot time, it is useful to have
a boot log from the live by adding ``live-boot.debug`` to the boot line at
grub:

* press an arrow key to stop the automatic boot;
* press ``e`` to edit the selected entry;
* change the ``linux ... --`` line to ``linux ... live-boot.debug --``;
* press ``ctrl-x`` or ``F10`` to start booting.

The log should appear in ``/var/log/live/boot.log``, but it is sometimes
hidden by the ``##log##`` partition; in that case it can be found e.g.
in ``/run/live/overlay/rw/var/log/live/boot.log``.

Unable to update cache after performing isolinux installation
-------------------------------------------------------------

If you get an error like this when building::

  INFO livewrapper Performing isolinux installation...
  Unable to update cache:

and your host system is configured to use a proxy for apt in
``/etc/apt/apt.conf.d/``, note that modian will use that setting, so it
may be the proxy that is causing the issue.

Notably, if you're using apt-cacher-ng, you may have to check that
you're using an http mirror in ``$MLW_MIRROR``, rather than an https
one, so that it can be properly cached.
