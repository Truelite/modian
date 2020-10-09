import os
import tempfile
import shutil
from .chroot import Chroot
from .component import Component


class Squashfs(Component):
    mksquashfs = shutil.which("mksquashfs")

    def __init__(self, sysdesc):
        super().__init__()
        self.sysdesc = sysdesc

    def build(self, dest):
        # with self.sysdesc.cache(dest, "squashfs", self.sysdesc.cache_id_squashfs) as cache:
        #     if not cache.hit:
        with self.work_dir(self.sysdesc.chroot_dir) as chroot_dir:
            chroot = Chroot(self.sysdesc)
            chroot.build(chroot_dir)
            if self.sysdesc.customize_squashfs:
                self.run_cmd([self.sysdesc.customize_squashfs, chroot_dir])
            self.run_mksquashfs(src=chroot_dir, dest=dest)

    def run_mksquashfs(self, src, dest):
        if not os.path.exists(dest):
            os.makedirs(dest)
        suffixed = os.path.join(dest, "filesystem.squashfs")
        if os.path.exists(suffixed):
            self.log.info("%s already exists: reusing it", suffixed)
            return

        with tempfile.NamedTemporaryFile(mode="wt") as fd:
            print("/proc", file=fd)
            print("/dev", file=fd)
            print("/sys", file=fd)
            print("/run", file=fd)

            self.log.info("Running mksquashfs on %s", src)
            self.run_cmd(
                ['nice', self.mksquashfs, src, suffixed,
                 '-no-progress', '-comp', self.sysdesc.squashfs_compression,
                 '-e', fd.name], eatmydata=False)
            check_size = os.path.getsize(suffixed)
            self.log.debug("Created squashfs: %s (%d bytes)", suffixed, check_size)
            if check_size < (1024 * 1024):
                self.log.warning(
                    "%s appears to be too small: %s bytes",
                    suffixed, check_size)

            bootdir = os.path.join(src, 'boot')
            # copying the boot/* files
            self.log.debug("Copying boot files out of squashfs")
            self.copy_files(bootdir, dest)

    def copy_files(self, src, dest):
        """
        Copy all files in src to dest
        """
        for filename in os.listdir(src):
            src_path = os.path.join(src, filename)
            if os.path.isdir(src_path) or os.path.islink(src_path):
                continue
            shutil.copyfile(
                src_path,
                os.path.join(dest, filename))
