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


class ActionNotImplementedError(NotImplementedError):
    """
    Exception raised when an action is still not implemented.
    """


class Actions:
    """
    Steps to manipulate the system during the installation.
    """

    def __init__(self, system, hardware):
        self.system = system
        self.hardware = hardware
        self.queue = []

    def run_action(self, action):
        try:
            getattr(self, action)()
        except AttributeError:
            raise ActionNotImplementedError()

    def do_nothing(self):
        print("I am doing nothing!")
        log.warning("And logging nothing!")
