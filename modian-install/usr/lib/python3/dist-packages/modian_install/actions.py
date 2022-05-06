import logging
import os
import subprocess


log = logging.getLogger()


class ModianError(RuntimeError):
    """
    Exception that gets caught to make the program exit with an error.

    Use this as a kind of RuntimeError where the user input or system
    configuration is likely to blame.
    """


class ActionNotImplementedError(NotImplementedError):
    """
    Exception raised when an action is still not implemented.
    """


class Actions:
    """
    Steps to manipulate the system during the installation.
    """

    def __init__(self, system, hardware, env_config):
        self.system = system
        self.hardware = hardware
        self.env_config = env_config
        self.queue = []

    def run_action(self, action):
        try:
            action_method = getattr(self, "do_" + action)
        except AttributeError as e:
            raise ActionNotImplementedError(e)
        log.info("Running action %s", action)
        action_method()

    def _stdout_lines_from_command(self, command):
        res = subprocess.run(command, stdout=subprocess.PIPE)
        for line in res.stdout.split(b"\n"):
            # we only provide lines with some content
            if line:
                yield line

    def do_clean_lvm_groups(self):
        for lv in self._stdout_lines_from_command(
            ["lvs", "--noheadings", "-o", "lvname"]
        ):
            log.info("removing %s logical volume", lv)
            subprocess.run(["lvremove", "-f", lv])
        for vg in self._stdout_lines_from_command(
            ["vgs", "--noheadings", "-o", "vgname"]
        ):
            log.info("removing %s volume group", vg)
            subprocess.run(["vgremove", "-f", vg])
        for pv in self._stdout_lines_from_command(
            ["pvs", "--noheadings", "-o", "pvname"]
        ):
            log.info("removing %s physical volume", pv)
            subprocess.run(["pvremove", "-f", pv])

    def do_format_part_root(self):
        part_root = os.path.join(
            "/dev",
            self.system.partitions[self.system.LABELS["root"]].dev,
        )
        self.hardware.format_device("##root##", part_root)
        if not self.hardware.uefi:
            # Install grub and initial system disk structure,
            log.info("Installing GRUB")
            self.hardware.run_cmd_stop_errors(["mount", part_root, "/mnt"])
            log.info("partition has been mounted")
            subprocess.run("mount")
            # Legacy system
            self.hardware.run_cmd_stop_errors([
                "grub-install",
                "--no-floppy",
                "--root-directory=/mnt",
                part_root
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
                self.env_config["modian_release_name"],
                "--isoimage", os.path.join("/dev", self.system.disk_inst.name),
                "--max-installed-versions={}".format(
                    self.env_config["max_installed_versions"]
                ),
                "--boot-append={}".format(
                    self.env.config["installed_boot_append"]
                ),
                "--systemd-target={}".format(
                    self.env.config["systemd_target"]
                ),
            ])
            subprocess.run(["umount", "/mnt"])

    def do_format_part_esp(self):
        part_esp = os.path.join(
            "/dev",
            self.system.partitions[self.system.LABELS["esp"]].dev,
        )
        part_root = os.path.join(
            "/dev",
            self.system.partitions[self.system.LABELS["root"]].dev,
        )
        log.info("%s: setting up ESP partition", part_esp)
        self.hardware.run_cmd_stop_errors(["mkfs.vfat", part_esp])

        if self.hardware.uefi:
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
                part_root
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
                self.env_config["modian_release_name"],
                "--isoimage", os.path.join("/dev", self.system.disk_inst.name),
                "--max-installed-versions={}".format(
                    self.env_config["max_installed_versions"]
                ),
                "--boot-append={}".format(
                    self.env.config["installed_boot_append"]
                ),
                "--systemd-target={}".format(
                    self.env.config["systemd_target"]
                ),
            ])
            self.hardware.run_cmd_stop_errors(["umount", "/boot/uefi"])
            self.hardware.run_cmd_stop_errors(["umount", "/mnt"])
