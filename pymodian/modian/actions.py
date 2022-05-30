from __future__ import annotations

import logging
import os
import subprocess
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from . import hardware
    from .config import Config

from .exceptions import ActionNotImplementedError


log = logging.getLogger()


class Actions:
    """
    Steps to manipulate the system during the installation.
    """

    def __init__(self,
                 system: hardware.System,
                 hardware: hardware.Hardware,
                 env_config: Config):
        self.system = system
        self.hardware = hardware
        self.env_config = env_config

    def run_action(self, action: str):
        try:
            action_method = getattr(self, "do_" + action)
        except AttributeError as e:
            raise ActionNotImplementedError(e)
        log.info("Running action %s", action)
        action_method()

    def _stdout_lines_from_command(self, command: List[str]):
        res = subprocess.run(command, stdout=subprocess.PIPE, check=True)
        for line in res.stdout.split(b"\n"):
            # we only provide lines with some content
            if line:
                yield line.decode()

    def do_clean_lvm_groups(self):
        for lv in self._stdout_lines_from_command(
                ["lvs", "--noheadings", "-o", "lvname"]):
            log.info("removing %s logical volume", lv)
            subprocess.run(["lvremove", "-f", lv])
        for vg in self._stdout_lines_from_command(
                ["vgs", "--noheadings", "-o", "vgname"]):
            log.info("removing %s volume group", vg)
            subprocess.run(["vgremove", "-f", vg])
        for pv in self._stdout_lines_from_command(
                ["pvs", "--noheadings", "-o", "pvname"]):
            log.info("removing %s physical volume", pv)
            subprocess.run(["pvremove", "-f", pv])

    def do_format_part_root(self, part_root: str = None):
        part_root = part_root or os.path.join(
            "/dev",
            self.system.partitions[self.system.LABELS["root"]].dev,
        )
        disk_root = os.path.join(
            "/dev",
            self.system.disk_root.name,
        )
        self.hardware.format_device("##root##", part_root)
        if not self.hardware.uefi:
            cfg = self.env_config
            # Install grub and initial system disk structure,
            log.info("Installing GRUB")
            self.hardware.run_cmd_stop_errors(["mount", part_root, "/mnt"])
            # Legacy system
            self.hardware.run_cmd_stop_errors([
                "grub-install",
                "--no-floppy",
                "--root-directory=/mnt",
                disk_root
            ])
            log.info("grub has been installed")
            # TODO: change this with the right python call
            self.hardware.run_cmd_stop_errors([
                "install",
                "-m", "0644",
                "/usr/share/grub/unicode.pf2", "/mnt/boot/grub"
            ])
            self.hardware.run_cmd_stop_errors([
                "modian-install-iso",
                "--live-dir=/mnt",
                "--no-check-integrity",
                self.env_config.modian_release_name,
                "--isoimage", os.path.join("/dev", self.system.disk_inst.name),
                f"--max-installed-versions={cfg.max_installed_versions}",
                f"--boot-append={cfg.installed_boot_append}",
                f"--systemd-target={self.env_config.systemd_target}",
            ])
            subprocess.run(["umount", "/mnt"])

    def do_format_part_esp(self, part_esp=None, part_root=None):
        part_esp = part_esp or os.path.join(
            "/dev",
            self.system.partitions[self.system.LABELS["esp"]].dev,
        )
        part_root = part_root or os.path.join(
            "/dev",
            self.system.partitions[self.system.LABELS["root"]].dev,
        )
        log.info("%s: setting up ESP partition", part_esp)
        self.hardware.run_cmd_stop_errors(["mkfs.vfat", part_esp])

        if self.hardware.uefi:
            cfg = self.env_config
            # Install grub and initial system disk structure,
            log.info("Installing GRUB")
            self.hardware.run_cmd_stop_errors(["mount", part_root, "/mnt"])
            os.makedirs("/boot/efi", exist_ok=True)
            self.hardware.run_cmd_stop_errors(["mount", part_esp, "/boot/efi"])

            # UEFI system
            self.hardware.run_cmd_stop_errors([
                "grub-install",
                "--no-floppy",
                "--efi-directory=/boot/efi",
                "--root-directory=/mnt",
                self.system.disk_root
            ])
            # TODO: change this with the right python call
            self.hardware.run_cmd_stop_errors([
                "install",
                "-m", "0644",
                "/usr/share/grub/unicode.pf2", "/mnt/boot/grub"
            ])
            self.hardware.run_cmd_stop_errors([
                "modian-install-iso",
                "--live-dir=/mnt",
                "--no-check-integrity",
                self.env_config.modian_release_name,
                "--isoimage", os.path.join("/dev", self.system.disk_inst.name),
                f"--max-installed-versions={cfg.max_installed_versions}",
                f"--boot-append={cfg.installed_boot_append}",
                f"--systemd-target={cfg.systemd_target}",
            ])
            self.hardware.run_cmd_stop_errors(["umount", "/boot/uefi"])
            self.hardware.run_cmd_stop_errors(["umount", "/mnt"])

    def do_format_part_log(self, part_log=None):
        part_log = part_log or os.path.join(
            "/dev",
            self.system.partitions[self.system.LABELS["log"]].dev,
        )
        self.hardware.format_device("##log##", part_log)

    def do_format_part_data(self, part_data=None):
        part_data = part_data or os.path.join(
            "/dev",
            self.system.partitions[self.system.LABELS["data"]].dev,
        )
        self.hardware.format_device("##data##", part_data)

        # Create initial directory structure
        self.hardware.run_cmd_stop_errors(["mount", part_data, "/mnt"])
        os.makedirs("/mnt/images/inkjet")
        os.makedirs("/mnt/cfast")
        self.hardware.run_cmd_stop_errors(["umount", "/mnt"])

    def do_setup_disk_root(self):
        disk_root = os.path.join(
            "/dev",
            self.system.disk_root.name,
        )
        log.info("%s: partitioning root disk", disk_root)

        if self.hardware.uefi:
            self.hardware.partition_disk(disk_root, "systemdisk-uefi")
        else:
            self.hardware.partition_disk(disk_root, "systemdisk-bios")

        self.do_format_part_root(
            self.hardware.get_partition_disk_name(disk_root, 1),
        )
        self.do_format_part_log(
            self.hardware.get_partition_disk_name(disk_root, 2),
        )
        if self.hardware.uefi:
            self.do_format_part_esp(
                self.hardware.get_partition_disk_name(disk_root, 4),
                self.hardware.get_partition_disk_name(disk_root, 1),
            )
