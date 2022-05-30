from __future__ import annotations
import argparse
import logging
import socket
import sys

# Used for the non-pythonic running of actions: remove these three after
# it has been completely converted.
import os
import subprocess

from typing import Dict, Optional, Type

from . import hardware, actions, exceptions
from .config import Config


log = logging.getLogger()


class InstallCommand:
    DESCRIPTION = "Perform the modian first install"
    VERSION = "1.0"

    HARDWARE_CLASS: Type[hardware.Hardware] = hardware.Hardware
    SYSTEM_CLASS: Type[hardware.System] = hardware.System
    ACTIONS_CLASS: Type[actions.Actions] = actions.Actions

    def get_parser(self):
        parser = argparse.ArgumentParser(description=self.DESCRIPTION)
        parser.add_argument(
            "--version",
            action="version",
            version="$(prog)s {}".format(self.VERSION),
        )
        parser.add_argument(
            "--debug", action="store_true", help="debugging output"
        )
        parser.add_argument(
            "-v", "--verbose", action="store_true", help="verbose output"
        )

        return parser

    def setup_logging(self):
        if self.args.debug:
            log_level = logging.DEBUG
        elif self.args.verbose:
            log_level = logging.INFO
        else:
            log_level = logging.WARN
        logging.basicConfig(
            level=log_level,
            stream=sys.stderr,
            format="%(asctime)s %(levelname)s %(message)s",
        )

    def setup(self,
              actions_class: Optional[Type[actions.Actions]] = None,
              system_class: Optional[Type[hardware.System]] = None):
        """
        Common command setup tasks including parsing arguments.

        This method should be called at the beginning of the main() of
        any derived class.

        This isn't done in the __init__() because this way it's easier
        to customize the class parameters.
        """

        self.parser = self.get_parser()
        self.args = self.parser.parse_args()
        self.setup_logging()

        self.env_config = self.read_configuration_from_env()

        self.hardware = self.HARDWARE_CLASS(env_config=self.env_config)

        if system_class is None:
            system_class = self.SYSTEM_CLASS
        self.system = system_class(hardware=self.hardware)

        if actions_class is None:
            actions_class = self.ACTIONS_CLASS
        self.actions = actions_class(
            system=self.system,
            hardware=self.hardware,
            env_config=self.env_config,
        )

    def read_configuration_from_env(self) -> Config:
        return Config(
            modian_release_name=os.environ["MODIAN_RELEASE_NAME"],
            modian_release_full_name=os.environ["MODIAN_RELEASE_FULL_NAME"],
            hostname=os.environ.get("HOSTNAME", socket.gethostname()),
            dir_bootscript=os.environ.get(
                "DIR_BOOTSCRIPT", "/etc/modian/boot.d"),
            systemd_target=os.environ.get("SYSTEMD_TARGET", "default.target"),
            installed_boot_append=os.environ.get("INSTALLED_BOOT_APPEND", ""),
            max_installed_versions=os.environ["MAX_INSTALLED_VERSIONS"],
            datadir=os.environ["DATADIR"],
        )

    def log_detection_report(self):
        """
        Print a report of found partitions.

        Override this method to add the custom partitions you need.
        """
        log.info("Detected system disk: {} ({})".format(
            self.system.disk_root.name,
            self.hardware.get_disk_model(self.system.disk_root.name),
        ))
        log.info("Detected USB disk: {} ({})".format(
            self.system.disk_inst.name,
            self.hardware.get_disk_model(self.system.disk_inst.name),
        ))

        log.info("Detected root partition: {}".format(
            self.system.partitions.get(self.system.LABELS["root"], "none"),
        ))
        log.info("Detected log partition: {}".format(
            self.system.partitions.get(self.system.LABELS["log"], "none"),
        ))

    def backup_partitions(self):
        """
        Override this to perform a backup of some data before installing.
        """

    def restore_partitions(self):
        """
        Override this to restore the backup performed earlier.
        """

    def prepare_installation(self):
        # TODO: migrate to here the miscellaneous steps in
        # do_first_install up to running the actions

        # tune2fs wants /etc/mtaFirst install a in order to run:
        # creating it if it is missing
        self.hardware.create_mtab()

        # In case booting detected a swap partition and enabled it,
        # disable all swap now so hard disks are not used anymore
        self.hardware.disable_swap()

        # Umount all partitions from the target drives
        self.system.umount_partitions_target_drives()

    def add_additional_environment(self) -> Dict[str, str]:
        """
        Override this method to add extra environment variables when running
        actions
        """
        return {}

    def run_actions(self):
        # TODO: as a first step, write a script that loads common.sh and
        # runs all actions and run it with subprocess
        env = os.environ.copy()
        env["DISK_ROOT"] = self.system.disk_root.name
        env["DISK_INST"] = self.system.disk_inst.name
        if self.system.LABELS["root"] in self.system.partitions:
            env["PART_ROOT"] = self.system.partitions[
                self.system.LABELS["root"]].dev
        if self.system.LABELS["log"] in self.system.partitions:
            env["PART_LOG"] = self.system.partitions[
                self.system.LABELS["log"]].dev
        if self.system.LABELS["esp"] in self.system.partitions:
            env["PART_ESP"] = self.system.partitions[
                self.system.LABELS["esp"]].dev
        env["ACTIONS"] = "{}".format(" ".join(self.action_list))

        env.update(self.add_additional_environment())

        for action in self.action_list:
            try:
                self.actions.run_action(action)
            except exceptions.ActionNotImplementedError:
                subprocess.run([
                    '/usr/sbin/modian-run-action',
                    action
                ], env=env, check=True)

    def main(self):
        self.setup()

        self.system.detect()
        self.log_detection_report()
        self.action_list = self.system.compute_actions()
        self.backup_partitions()
        self.prepare_installation()
        self.run_actions()
        self.restore_partitions()
