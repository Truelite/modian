************
 Local Repo
************

modian-live-wrapper needs an apt repository to install the modian-*
packages from; this directory includes a sample reprepro configuration
and helper script to quickly setup, serve and then teardown such a
repository on the local machine for development.

The reprepro configuration can also be used as a starting point for long
term infrastructure.

See also
--------

https://wiki.debian.org/DebianRepository/SetupWithReprepro
   How to set up a personal repository with reprepro, including key
   signatures and apache to serve it.
https://manpages.debian.org/unstable/reprepro/reprepro.1.en.html
   Reprepro manpage.
