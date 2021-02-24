*************
 Development
*************

``local-repo``
==============

``local-repo`` is a tool to create and manage a simple local apt
repository suitable to provide copies of locally modified packages to
``modian-live-wrapper``.

Installation
------------

``local-repo`` can be run in-place and its dependencies are just
``reprepro`` and the Python 3 standard library.

Usage
-----

To create an apt repository in the directory ``repo``::

   ./local-repo.py create

To add a package to the repository::

   ./local-repo.py add-deb path/to/package.deb

To serve the apt repository on port 8099::

   ./local-repo.py serve
