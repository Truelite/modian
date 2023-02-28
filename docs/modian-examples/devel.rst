*************
 Development
*************

Building packages
=================

Most modian components include the needed configuration to build source
and binary packages in their ``debian/`` subdirectory.

Those packages can be built using any one of the systems commonly used
to build debian packages; it is recommended to use a method that builds
inside a clean chroot such as pbuilder/cowbuilder or sbuild.

See also :ref:`local-repo <local_repo>` to publish deb packages in a
local repository.

Temporary project customizations
================================

When building a project with the :samp:`build_{<project name>}` script
you may want to change some parameters such as the apt mirror to use:
see :ref:`build_script` for details on the available variables.

To run lwr in-place, getting the packages from local-repo, you may want
to run the script as::

   [sudo] MODIAN_LWR=path/to/modian/modian-live-wrapper/lwr.py \
          MLW_EXTRA_VARS=ansible/extra_vars_in_place.yaml \
          ./build_example

Custom ansible variables
------------------------

``modian-lwr`` loads a yaml file with custom variables that are passed
to ansible; this can be used to change further configurations when
building from the git checkout during development.

For example, in ``modian-full-example`` ansible uses a ``modian_repo``
variable to configure a repository to get modian packages from, and the
file ``ansible/extra_vars_in_place.yaml`` sets that variable to use the
repository served by ``local_repo.py``.
