import argparse
import logging
import sys

from . import hardware, actions


log = logging.getLogger()


class InstallCommand:
    DESCRIPTION = "Perform the modian first install"
    VERSION = "1.0"

    HARDWARE_CLASS = hardware.Hardware
    SYSTEM_CLASS = hardware.System

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

    def setup(self, actions_class=None, system_class=None):
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

        self.hardware = hardware.Hardware()

        if actions_class is None:
            actions_class = actions.Actions
        self.actions = actions_class(hardware=self.hardware)

        if system_class is None:
            system_class = hardware.System
        self.system = system_class(hardware=self.hardware)

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

    def main(self):
        self.setup()

        self.hardware = self.HARDWARE_CLASS()
        self.system = self.SYSTEM_CLASS(self.hardware)
        self.system.detect()
        self.log_detection_report()
