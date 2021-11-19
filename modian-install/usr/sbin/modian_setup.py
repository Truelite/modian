#!/usr/bin/env python3

import logging
import sys

import modian_install


log = logging.getLogger()


if __name__ == "__main__":
    try:
        modian_install.command.InstallCommand().main()
    except modian_install.actions.ModianError as e:
        log.error("%s", e)
        sys.exit(1)
