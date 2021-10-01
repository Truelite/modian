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
    def main(self):
        self.setup()

        hardware = modian_install.hardware.Hardware()
        system = System(hardware)
        system.detect()

        def print_env(k, v):
            print("{}={}".format(k, shlex.quote(v)))

        print_env("DISK_ROOT", system.disk_root.name)
        print_env("DISK_INST", system.disk_inst.name)
        if system.LABELS["root"] in system.partitions:
            print_env("PART_ROOT", system.partitions[system.LABELS["root"]].dev)
        if system.LABELS["log"] in system.partitions:
            print_env("PART_LOG", system.partitions[system.LABELS["log"]].dev)
        if system.LABELS["data"] in system.partitions:
            print_env("PART_DATA", system.partitions[system.LABELS["data"]].dev)
        if system.LABELS["esp"] in system.partitions:
            print_env("PART_ESP", system.partitions[system.LABELS["esp"]].dev)
        print("ACTIONS={}".format(shlex.quote(" ".join(system.compute_actions()))))


def main():
    import argparse

    hardware = modian_install.hardware.Hardware()
    system = System(hardware)
    system.detect()

    def print_env(k, v):
        print("{}={}".format(k, shlex.quote(v)))

    print_env("DISK_ROOT", system.disk_root.name)
    if system.disk_img is not None:
        print_env("DISK_IMG", system.disk_img.name)
    else:
        print_env("DISK_IMG", "")
    print_env("DISK_INST", system.disk_inst.name)
    if LABEL_ROOT in system.partitions:
        print_env("PART_ROOT", system.partitions[LABEL_ROOT].dev)
    if LABEL_LOG in system.partitions:
        print_env("PART_LOG", system.partitions[LABEL_LOG].dev)
    if LABEL_DATA in system.partitions:
        print_env("PART_DATA", system.partitions[LABEL_DATA].dev)
    if LABEL_IMAGES in system.partitions:
        print_env("PART_IMAGES", system.partitions[LABEL_IMAGES].dev)
    if LABEL_ESP in system.partitions:
        print_env("PART_ESP", system.partitions[LABEL_ESP].dev)
    print("ACTIONS={}".format(shlex.quote(" ".join(system.compute_actions()))))


if __name__ == "__main__":
    try:
        Command().main()
    except modian_install.actions.ModianError as e:
        log.error("%s", e)
        sys.exit(1)
