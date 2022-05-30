#!/usr/bin/env python3

import logging
import sys

import modian


log = logging.getLogger()


if __name__ == "__main__":
    try:
        modian.command.InstallCommand().main()
    except modian.actions.ModianError as e:
        log.error("%s", e)
        sys.exit(1)
