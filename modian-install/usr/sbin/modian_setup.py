#!/usr/bin/env python3

import logging
import sys

import modian_install


log = logging.getLogger()


class Command(modian_install.command.InstallCommand):
    def main(self):
        self.setup()

        self.hardware = modian_install.hardware.Hardware()
        self.system = modian_install.hardware.System(self.hardware)
        self.system.detect()
        self.print_detection_report()


if __name__ == "__main__":
    try:
        Command().main()
    except modian_install.actions.ModianError as e:
        log.error("%s", e)
        sys.exit(1)
