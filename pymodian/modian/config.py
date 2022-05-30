from __future__ import annotations

from typing import NamedTuple


class Config(NamedTuple):
    """
    Runtime configuration for modian-install
    """
    modian_release_name: str
    modian_release_full_name: str
    hostname: str
    dir_bootscript: str
    systemd_target: str
    installed_boot_append: str
    max_installed_versions: str
    datadir: str
