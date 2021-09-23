import logging
import os
import re
import subprocess

log = logging.getLogger()


class Hardware:
    """
    Hardware detection and operations
    """

    def __init__(self):
        # In bash this was ``if efibootmgr > /dev/null 2>&1``
        self.uefi = False
        try:
            res = subprocess.run('efibootmgr')
            if res.returncode == 0:
                self.uefi = True
        except FileNotFoundError:
            pass
