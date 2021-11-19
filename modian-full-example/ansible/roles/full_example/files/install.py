#!/usr/bin/python3

import logging
import sys
import os
import re
import shlex

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


class Command(modian_install.command.InstallCommand):
    SYSTEM_CLASS = System

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

    def main(self):
        super().main()

        def print_env(k, v):
            print("{}={}".format(k, shlex.quote(v)))

        print_env("DISK_ROOT", self.system.disk_root.name)
        print_env("DISK_INST", self.system.disk_inst.name)
        if self.system.LABELS["root"] in self.system.partitions:
            print_env("PART_ROOT", self.system.partitions[self.system.LABELS["root"]].dev)
        if self.system.LABELS["log"] in self.system.partitions:
            print_env("PART_LOG", self.system.partitions[self.system.LABELS["log"]].dev)
        if self.system.LABELS["data"] in self.system.partitions:
            print_env("PART_DATA", self.system.partitions[self.system.LABELS["data"]].dev)
        if self.system.LABELS["esp"] in self.system.partitions:
            print_env("PART_ESP", self.system.partitions[self.system.LABELS["esp"]].dev)
        print("ACTIONS={}".format(shlex.quote(" ".join(self.actions))))




if __name__ == "__main__":
    try:
        Command().main()
    except modian_install.actions.ModianError as e:
        log.error("%s", e)
        sys.exit(1)
