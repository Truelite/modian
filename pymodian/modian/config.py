from __future__ import annotations

import dataclasses
import os
import socket

from typing import NamedTuple

import ruamel.yaml


@dataclasses.dataclass
class Config():
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
    extra_config: list = dataclasses.field(default_factory=list)

    def load(self) -> bool:
        res = []
        res.append(self.load_yaml("/etc/modian/config.yaml"))
        for conf_file in self.extra_config:
            res.append(self.load_yaml(conf_file))
        res.append(self.load_env())
        return any(res)

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
        for f in dataclasses.fields(self):
            if data.get(f.name, None) is not None:
                setattr(self, f.name, data[f.name])
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
        for f in dataclasses.fields(self):
            if getattr(self, f.name) is None:
                missing.append(f.name)

        return missing
