***************
 Configuration
***************

``modian-install`` installs a configuration file
``/etc/modian/config.sh`` that is sourced during the installation; this
should be installed on the live image and thus will have to be edited
using the ansible playbook.

The following variables need to be set:

``MODIAN_RELEASE_NAME``
   ;
``MODIAN_RELEASE_FULL_NAME``
   ;

Other variables used by ``modian-install`` can be overriden in the same
file, notable ones include:

``VERBOSE``
   set to ``yes`` to enable verbose output;

``MAX_INSTALLED_VERSIONS``
   the number of version that are kept when updating modian. Default is 3.
