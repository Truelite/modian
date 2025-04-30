**************
 Requirements
**************

Building a modian image requires a Debian system [#derivatives]_ and
either the package modian-live-wrapper installed systemwide, or its
dependencies and a checkout of the modian git repository.

``ansible-core >= 2.15`` is required because of the deb822_repository
module: this is available in Debian trixie, but adding locally just that
module (from a more recent release) to
``/root/.ansible/plugins/modules/`` seems to work on bookworm.

.. [#derivatives] Debian derivatives probably also work, but are
   currently not tested / supported.

Building requires using the root user.
