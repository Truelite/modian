import argparse
import logging
import sys

from . import hardware, actions


class InstallCommand:
    DESCRIPTION = "Perform the modian first install"
    VERSION = "1.0"

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

    def setup(self, actions_class=None):
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

        self.hardware = hardware.Hardware(uefi=self.args.uefi)
        if not actions_class:
            actions_class = actions.Actions
        self.actions = actions_class(hardware=self.hardware)

    def main(self):
        raise NotImplementedError()
