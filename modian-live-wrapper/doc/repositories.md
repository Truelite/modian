# Package repositories

Package repositories used to build the image do not need to be the same as
those configured inside the image. This allows, for example, to build an image
that uses standard repositories once it is run, but it is built using faster
local mirrors.

The command-line option `--mirror` controls what mirror is used by debootstrap
at build time.

The command-line options `--apt-mirror` and `--apt-mirror-components` controls
what mirror is configured in the resulting live image.

When [ansible](ansible.md) runs, only `--mirror` is configured, limited to the
`main` component, and you can use ansible rules to add extra repositories.

Any extra repository added as `/etc/apt/sources.list.d/inst-*` will be removed
at the end of the build. You can take advantage of this using the `filename`
option of the `apt_repository` playbook rule to distinguish which mirrors you
are adding for the build process, and which you are adding to be configured in
the resulting live system.

Note that the file `/etc/apt/sources.list` is also deleted at the end of the
build, and the `--apt-mirror` source is added as
`/etc/apt/sources.list.d/base.list`.
