import hashlib
import json
import shutil
import os
import contextlib
from .component import Component
from .squashfs import Squashfs


class BaseSystem(Component):
    """
    Description of the base system to be built
    """
    # Base distribution
    distribution = "stable"

    # Architecture of the base distribution
    architecture = None

    # Mirror used for building the base distribution
    build_mirror = "http://deb.debian.org/debian/"

    # Mirror configured in the target distribution
    installed_mirror = "http://deb.debian.org/debian/"

    # Components activated for the installed mirror
    installed_mirror_components = "main"

    # Ansible playbook used for customization
    playbook = "chroot.yaml"

    # Packages to install in the chroot
    packages = []

    # Name (without version) of the kernel package to use
    kernel_package = None

    # Compression to use for the squashfs
    squashfs_compression = "lzo"  # TODO: default to xz

    # Enable systemd-networkd
    networkd = False

    # Directory where partial artifacts can be cached
    cache_dir = None

    # Script to run before generating the squashfs
    customize_squashfs = None

    # Chroot working directory (by default, use a temporary directory)
    chroot_dir = None

    # Directory where ansible configuration is stored (by default, use a temporary directory)
    ansible_dir = None

    def __init__(self, **kw):
        super().__init__()
        for k, v in kw.items():
            setattr(self, k, v)
        self.packages.append("python3")  # for ansible
        self.packages.append("eatmydata")  # to run ansible under eatmydata
        self.packages = sorted(set(self.packages))

    @property
    def cache_id_debootstrap(self):
        info = {"arch": self.architecture, "dist": self.distribution, "bm": self.build_mirror, "pkgs": sorted(self.packages)}
        sha = hashlib.sha1()
        self.log.debug("cache key for debootstrap: %s", json.dumps(info, sort_keys=True))
        sha.update(json.dumps(info, sort_keys=True).encode("utf8"))
        return sha.hexdigest()

    @property
    def cache_id_chroot(self):
        info = {"debootstrap": self.cache_id_debootstrap,
                "playbook": self.playbook}
        sha = hashlib.sha1()
        self.log.debug("cache key for chroot: %s", json.dumps(info, sort_keys=True))
        sha.update(json.dumps(info, sort_keys=True).encode("utf8"))
        return sha.hexdigest()

    @property
    def cache_id_squashfs(self):
        info = {"debootstrap": self.cache_id_debootstrap,
                "im": self.installed_mirror, "playbook": self.playbook,
                "comp": self.squashfs_compression, "networkd": self.networkd}
        sha = hashlib.sha1()
        self.log.debug("cache key for squashfs: %s", json.dumps(info, sort_keys=True))
        sha.update(json.dumps(info, sort_keys=True).encode("utf8"))
        return sha.hexdigest()

    def to_dict(self, include=None, exclude=None):
        res = {}
        for field in "distribution", "architecture", "build_mirror", "installed_mirror", "playbook", "squashfs_compression", "kernel_package":
            if exclude and field in exclude:
                continue
            if include and field not in include:
                continue
            res[field] = getattr(self, field)
        return res

    @contextlib.contextmanager
    def cache(self, path, name, cache_id):
        if not self.cache_dir:
            yield NullCacher(path)
            return

        os.makedirs(self.cache_dir, exist_ok=True)
        cacher = Cacher(self, os.path.join(self.cache_dir, name + "-" + cache_id + ".tar.gz"), path)

        if cacher.hit:
            self.log.info("%s found: reusing it", cacher.tarball_name)
            cacher.extract()
            yield cacher
        else:
            self.log.info("%s not found: (re)creating it", cacher.tarball_name)
            yield cacher
            cacher.store()

    def build(self, dest):
        with umask(0o022):
            squashfs = Squashfs(self)
            squashfs.build(dest)


class NullCacher:
    def __init__(self, path):
        self.path = path
        self.hit = False

    def extract(self):
        pass

    def store(self):
        pass


class Cacher:
    def __init__(self, sysdesc, tarball_name, path):
        self.sysdesc = sysdesc
        self.tarball_name = tarball_name
        self.path = path
        self.hit = os.path.exists(self.tarball_name)

    def extract(self):
        if os.path.isdir(self.path):
            shutil.rmtree(self.path)
        os.makedirs(self.path)
        self.sysdesc.run_cmd(["tar", "-C", self.path, "-zxf", self.tarball_name], eatmydata=False)

    def store(self):
        self.sysdesc.run_cmd(["tar", "-C", self.path, "-zcf", self.tarball_name, "."], eatmydata=False)


@contextlib.contextmanager
def umask(mask):
    old_mask = os.umask(mask)
    yield
    os.umask(old_mask)
