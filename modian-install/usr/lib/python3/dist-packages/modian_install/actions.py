import logging
import os
import re
import subprocess


log = logging.getLogger()


class ModianError(RuntimeError):
    """
    Exception that gets caught to make the program exit with an error.

    Use this as a kind of RuntimeError where the user input or system
    configuration is likely to blame.
    """


class Actions:
    """
    Steps to manipulate the system during the installation.
    """

    def __init__(self, hardware):
        self.hardware = hardware
