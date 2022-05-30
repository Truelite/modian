from __future__ import annotations

from typing import NamedTuple, Optional


class Config(NamedTuple):
    """
    Runtime configuration for modian-install
    """
    modian_release_name: Optional[str]
    modian_release_full_name: Optional[str]
    hostname: Optional[str]
    dir_bootscript: Optional[str]
    systemd_target: Optional[str]
    installed_boot_append: Optional[str]
    max_installed_versions: Optional[str]
    datadir: str
