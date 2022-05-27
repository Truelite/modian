#!/usr/bin/python3

import logging
import os
import sys

import modian_install

log = logging.getLogger()

VERSION = "1.0"


class System(modian_install.hardware.System):
    def __init__(self, hardware):
        super().__init__(hardware)
        self.disk_img = None

        self.LABELS["data"] = "##data##"

    def read_additional_partition_labels(self):
        ok = True
        ok = self._check_partition(self.LABELS["data"], self.disk_root) and ok
        return ok

    def log_found_devices(self):
        log.info(
            "Root device: %s (%s)", self.disk_root.name, self.disk_root.details
        )
        log.info(
            "Installation media: %s (%s)",
            self.disk_inst.name,
            self.disk_inst.details,
        )

        self._read_partition_labels()
        log.info(
            "Partition %s: %s",
            self.LABELS["root"],
            self.partitions.get(self.LABELS["root"], None),
        )
        log.info(
            "Partition %s: %s",
            self.LABELS["log"],
            self.partitions.get(self.LABELS["log"], None)
        )
        log.info(
            "Partition %s: %s",
            self.LABELS["data"],
            self.partitions.get(self.LABELS["data"], None),
        )
        log.info(
            "Partition %s: %s",
            self.LABELS["esp"],
            self.partitions.get(self.LABELS["esp"], None)
        )

    def check_additional_root_disk_partitions(self):
        missing = []
        if self.LABELS["data"] not in self.partitions:
            missing.append(self.LABELS["data"])
        return missing

    def compute_additional_root_disk_partition_actions(self):
        return ["format_part_data"]


class Actions(modian_install.actions.Actions):
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

    def do_format_part_images(self, part_images=None):
        part_images = part_images or os.path.join(
            "/dev",
            self.system.partitions[self.system.LABELS["images"]].dev,
        )
        self.hardware.format_device("##images##", part_images)

    def do_setup_disk_root(self):
        super().do_setup_disk_root()
        disk_root = os.path.join(
            "/dev",
            self.system.disk_root.name,
        )
        self.do_format_part_data(
            self.hardware.get_partition_disk_name(disk_root, 3),
        )

    def do_setup_disk_images(self):
        if not self.system.disk_img:
            return
        disk_img = os.path.join(
            "/dev",
            self.system.disk_img.name,
        )
        log.info("%s: partitioning images disk", disk_img)
        self.do_format_part_images(
            self.hardware.get_partition_disk_name(disk_img, 1),
        )


class Command(modian_install.command.InstallCommand):
    SYSTEM_CLASS = System
    ACTIONS_CLASS = Actions

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
        log.info("Detected data partition: {}".format(
            self.system.partitions.get(self.system.LABELS["data"], "none"),
        ))

    def add_additional_environment(self):
        env = {}
        if self.system.LABELS["data"] in self.system.partitions:
            env["PART_DATA"] = self.system.partitions[
                self.system.LABELS["data"]
            ].dev
        return env


if __name__ == "__main__":
    try:
        Command().main()
    except modian_install.actions.ModianError as e:
        log.error("%s", e)
        sys.exit(1)
