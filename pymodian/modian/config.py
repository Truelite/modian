from __future__ import annotations

import os
import socket

from typing import NamedTuple

import ruamel.yaml


class Config(NamedTuple):
    """
    Runtime configuration for modian-install
    """
    modian_release_name: str = None
    modian_release_full_name: str = None
    hostname: str = socket.gethostname()
    dir_bootscript: str = "/etc/modian/boot.d"
    systemd_target: str = "default.target"
    installed_boot_append: str = ""
    max_installed_versions: str = "3"
    datadir: str = None

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

    def load_yaml(self, fname) -> bool:
        """
        Load values from a yaml file, if available.

        Overrides the current values.
        """
        if not os.path.exists(fname):
            return False

        res = False
        yaml = ruamel.yaml.YAML(typ="safe")
        with open(fname, "r") as fp:
            data = yaml.load(fp)
        for f in self._fields:
            if data[f]:
                self.setattr(f, data[f])
                res = True
        return res

    def load_env(self) -> bool:
        """
        Load values from environment variables, if available.

        Overrides the current values.
        """
        res = False
        for dest, var in [
            ("modian_release_name", "MODIAN_RELEASE_NAME"),
            ("modian_release_full_name", "MODIAN_RELEASE_FULL_NAME"),
            ("hostname", "HOSTNAME"),
            ("dir_bootscript", "DIR_BOOTSCRIPT"),
            ("systemd_target", "SYSTEMD_TARGET"),
            ("installed_boot_append", "INSTALLED_BOOT_APPEND"),
            ("max_installed_versions", "MAX_INSTALLED_VERSIONS"),
            ("datadir", "DATADIR"),
        ]:
            value = os.environ.get(var)
            if value:
                setattr(self, dest, value)
                res = True
        return res

    def check(self) -> list:
        """
        Check that all fields are set.

        Returns missing fields.
        """
        missing = []
        for f in self._fields:
            if getattr(self, f) is None:
                missing.append(f)

        return missing
