#!/usr/bin/env python3

import logging
import sys

import modian_install


log = logging.getLogger()


class Command(modian_install.command.InstallCommand):
    def main(self):
        self.setup()


if __name__ == "__main__":
    try:
        Command().main()
    except modian_install.actions.ModianError as e:
        log.error("%s", e)
        sys.exit(1)
