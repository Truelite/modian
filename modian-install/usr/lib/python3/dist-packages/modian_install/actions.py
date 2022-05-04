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
            action_method = getattr(self, "do_" + action)
        except AttributeError as e:
            raise ActionNotImplementedError(e)
        log.info("Running action %s", action)
        action_method()

    def _stdout_lines_from_command(self, command):
        res = subprocess.run(command, stdout=subprocess.PIPE)
        for line in res.stdout.split(b"\n"):
            # we only provide lines with some content
            if line:
                yield line

    def do_clean_lvm_groups(self):
        for lv in self._stdout_lines_from_command(
            ["lvs", "--noheadings", "-o", "lvname"]
        ):
            log.info("removing %s logical volume", lv)
            subprocess.run(["lvremove", "-f", lv])
        for vg in self._stdout_lines_from_command(
            ["vgs", "--noheadings", "-o", "vgname"]
        ):
            log.info("removing %s volume group", vg)
            subprocess.run(["vgremove", "-f", vg])
        for pv in self._stdout_lines_from_command(
            ["pvs", "--noheadings", "-o", "pvname"]
        ):
            log.info("removing %s physical volume", pv)
            subprocess.run(["pvremove", "-f", pv])
