***************
Troubleshooting
***************

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
