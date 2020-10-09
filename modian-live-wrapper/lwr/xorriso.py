# live-wrapper - Wrapper for vmdebootstrap for creating live images
# (C) Iain R. Learmonth 2015 <irl@debian.org>
# See COPYING for terms of usage, modification and redistribution.
#
# lwr/xorriso.py - xorriso helpers

"""
The lwr.xorriso module provides helpers for calling xorriso as part of the
image creation process.

.. note:: This module requires that the vmdebootstrap modules be available in
          the Python path.
"""

from lwr.utils import Fail
from .component import Component
import os
import shlex

# pylint: disable=missing-docstring,superfluous-parens


class Xorriso(Component):
    """
    This class acts as a wrapper for ``xorriso`` and allows for the command
    line arguments passed to be built based on the settings given to the main
    application.
    """

    def __init__(self, image_output, volume_id, isolinux=True, grub=True):
        super().__init__()
        self.image_output = image_output
        self.volume_id = volume_id
        self.isolinux = isolinux
        self.grub = grub
        self.args = ['xorriso']

    def build_args(self, cdroot):
        if len(self.args) > 1:
            Fail("Attempted to rebuild xorriso arguments while nthey are already defined!")
        self.args.extend(['-outdev', self.image_output])
        self.args.extend(['-volid', self.volume_id])
        self.args.extend(['-padding', '0'])
        self.args.extend(['-map', cdroot, '/'])
        self.args.extend(['-chmod', '0755', '/', '--'])

        if self.isolinux:
            self.args.extend(['-boot_image', 'isolinux', 'dir=/isolinux',
                              '-boot_image', 'isolinux',
                              'system_area=/usr/lib/ISOLINUX/isohdpfx.bin'])

        if self.grub:
            self.args.extend(['-boot_image', 'any', 'next',
                              '-boot_image', 'any', 'efi_path=boot/grub/efi.img',
                              '-boot_image', 'isolinux', 'partition_entry=gpt_basdat'])

        return self.args

    def write_run_script(self, dest):
        with open(dest, "wt") as fd:
            print("#!/bin/sh", file=fd)
            print(" ".join(shlex.quote(x) for x in self.args), file=fd)
        os.chmod(dest, 0o755)

    def build_image(self):
        """
        This will call ``xorriso`` with the arguments built.

        .. note::
            :any:`Xorriso.build_args` must have been called before
            calling :any:`Xorriso.build_image`.

        .. warning::
            The ``xorriso`` binary must be present in the current PATH.
        """
        if len(self.args) == 1:
            Fail("Attempted to run xorriso before building arguments!")
        self.run_cmd(self.args)
