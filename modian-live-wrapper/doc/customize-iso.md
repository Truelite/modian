# Extra iso customizations

You can use `--customize-iso` to run a command (usually a shellscript)
on the unpacked iso contents just before the .iso file is built with xorriso.

The script is passed the path to the directory with the unpacked iso contents
as the first and only argument.

For example:

```
#!/bin/sh

# $1 is the path to the root of the iso contents

set -ue

# Find the source directory from the script name
srcdir=$(dirname $0)

# Copy extra content into the final image
tar -C ${srcdir}/includes.binary -cf - . | tar -C $1 -xf -

# Compute and add a file with checksums for the individual components of the
# live system
(cd $1 && sha512sum ./live/* > sha512sum.txt)
```
