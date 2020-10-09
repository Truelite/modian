from .component import Component


class Debootstrap(Component):
    def __init__(self, sysdesc):
        super().__init__()
        self.sysdesc = sysdesc

    def build(self, dest):
        self.log.info("Debootstrapping %s [%s]", self.sysdesc.distribution, self.sysdesc.architecture)
        with self.sysdesc.cache(dest, "debootstrap", self.sysdesc.cache_id_debootstrap) as cache:
            if not cache.hit:
                args = ['debootstrap', '--arch=' + self.sysdesc.architecture]
                if self.sysdesc.packages:
                    args.append('--include=' + ','.join(sorted(self.sysdesc.packages)))
                args += [self.sysdesc.distribution, cache.path, self.sysdesc.build_mirror]
                self.log.debug("debootstrap arguments: %s", args)
                self.run_cmd(args)
                self.apt_clean_cache(cache.path)

    def apt_clean_cache(self, dest):
        self.run_cmd(['chroot', dest, 'apt-get', 'clean'])
