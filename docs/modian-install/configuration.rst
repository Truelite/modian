***************
 Configuration
***************

``modian-install`` installs two configuration files,
``/etc/modian/config.yaml``, read during the installation and
``/etc/modian/config.sh``, which is sourced before the environment is
read.

THey should be installed on the live image and will have to be edited
using the ansible playbook.

``/etc/modian/config.yaml`` is read first and has a list of additional
configuration files that will be read later and can overrdide its
values.

Finally, the environment variables are read, and will override the
values seen up to this point.


The following variables need to be set:

``modian_release_name`` (``MODIAN_RELEASE_NAME``)
   ;
``modian_release_full_name`` (``MODIAN_RELEASE_FULL_NAME``)
   ;

Other variables used by ``modian-install`` can be overriden in the same
file, notable ones include:

``VERBOSE``
   set to ``yes`` to enable verbose output;

``max_installed_versions`` (``MAX_INSTALLED_VERSIONS``)
   the number of version that are kept when updating modian. Default is 3;
``extra_config``
   a list of other configuration files to read: this can only be set in
   the first file (``/etc/modian/config.yaml``, as further values will
   be read, but ignored.
