******************
 Development tips
******************

Build speed and squashfs compression
====================================

``mksquashfs`` could be slow with the ``xz`` compression, and to speed
up development ``modian-live-wrapper`` defaults to ``lzo``. To produce
smaller images, you can switch to ``--squashfs-comp=xz`` on your final
builds.

Use of ``--cache-dir``
======================

Using ``--cache-dir`` can speed up repeated builds significantly, by
saving a tarball of the chroot system after running ``debootstrap`` and
after running ``ansible``. The tarball will be saved adding a hash of
the configuration arguments that influenced its creation, and it will be
reused when those configuration arguments are the same.

Ansible will be re-run every time even if its previous run results have
been cached, but it will be faster since it won’t have to redo things.
This allows changing the playbook contents without triggering a full
rerun of all the ansible playbooks.

Note that this caching mechanism is not infallible: it cannot detect,
for example, changes in the contents of the repository used by
debootstrap, or ansible rules that have been removed. The cached
tarballs are very useful in tight development iterations, but you may
want to make a final build without the cache directories (or deleting
their contents) to make sure none of those issues have crept in.

Debugging and ``--work-dir``
============================

If things go wrong, you can use ``--work-dir`` you get a nice directory
tree with all the intermediate steps available for your inspection:

* ``chroot`` is the chroot system that will eventually get compressed
  into a squashfs image. You can ``chroot(8)`` into it to try things
  out.
* ``ansible`` is the ansible configuration used to customize the chroot.
  It includes an ``ansible.sh`` script that you can run yourself to call
  ansible with the same options ``modian-live-wrapper`` uses, to
  conveniently debug your ansible rules without calling
  ``modian-live-wrapper`` all the time.
* ``iso`` are the unpacked contents of the iso image.
* ``xorriso.sh`` is the command used by ``modian-live-wrapper`` to
  generate the iso image from the ``iso/`` directory contents. You can
  run this script manually to debug issues with iso image creation.

You can also use ``--retry`` to reuse the contents of an existing work
directory, continuing a ``modian-live-wrapper`` invocation that got
interrupted for some reason. Note that using ``--retry`` means that a
partially build part of the build directory may stay partially built, as
``modian-live-wrapper`` has no way of detecting what had potentially
failed in a previous run.
