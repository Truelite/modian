# live-wrapper - Wrapper for vmdebootstrap for creating live images
# (C) Iain R. Learmonth 2015 <irl@debian.org>
# See COPYING for terms of usage, modification and redistribution.
#
# lwr/isolinux.py - ISOLINUX helpers

"""
The lwr.isolinux module contains helpers for isolinux including the
installation of isolinux files to the cdroot and the generation of the
isolinux.cfg files.
Directory listing of /isolinux/
advanced.cfg boot.cat hdt.c32 install.cfg isolinux.bin isolinux.cfg
ldlinux.c32 libcom32.c32 libutil.c32 live.cfg menu.cfg splash.png
stdmenu.cfg vesamenu.c32
"""

import os
import shutil
import tempfile
import re
from lwr.utils import Fail
from lwr.apt_udeb import get_apt_handler
from lwr.component import Component

# pylint: disable=missing-docstring


class Isolinux(Component):
    def __init__(self, work_dir=None):
        super().__init__()
        self.work_dir_path = work_dir

    def generate_cfg(self, bootconfig, submenu=False):
        ret = str()
        if not submenu:
            first = True
            ret += "INCLUDE stdmenu.cfg\n"
            ret += "MENU title Main Menu\n"
        else:
            first = False

        for entry in bootconfig.entries:
            label = "%s" % (entry['description'],)
            if entry['type'] == 'menu':
                if entry['subentries'].is_empty(["menu", "linux", "linux16", "com32"]):
                    continue
                ret += "MENU begin advanced\n"
                ret += "MENU title %s\n" % (label,)
                ret += self.generate_cfg(entry['subentries'], submenu=True)
                ret += " LABEL mainmenu \n "
                ret += " MENU label Back\n "
                ret += " MENU exit\n "
                ret += " MENU end\n "

            # do not want to default to menus
            if first:
                ret += "DEFAULT %s\n" % (label,)
                first = False
            if entry['type'].startswith('linux') or entry['type'] == 'com32':
                ret += "LABEL %s\n" % (label,)
                ret += "  SAY \"Booting %s...\"\n" % (entry['description'],)
                ret += "  %s %s\n" % (entry['type'], entry['kernel'],)
                if entry.get('initrd') is not None:
                    ret += "  APPEND initrd=%s %s\n" % (entry['initrd'], entry.get('cmdline', ''),)
                elif entry.get('cmdline') is not None:
                    ret += "  APPEND %s\n" % (entry['cmdline'],)
            ret += "\n"

        return ret

    def install(self, cdroot, mirror, suite, architecture, bootconfig):
        """
        Download and unpack the correct syslinux-common
        and isolinux packages for isolinux support.
        ISOLINUX looks first in boot/isolinux/ then isolinux/ then /
        This function puts all files into isolinux/
        """
        with self.work_dir(self.work_dir_path) as destdir:
            handler = get_apt_handler(destdir, mirror, suite, architecture)
            filename = handler.download_package('syslinux-common', destdir)
            if not filename:
                handler.clean_up_apt()
                raise Fail('Unable to download syslinux-common')
            # these files are put directly into cdroot/isolinux
            syslinux_files = [
                'ldlinux.c32', 'libcom32.c32', 'vesamenu.c32',
                'libutil.c32', 'libmenu.c32', 'libgpl.c32', 'hdt.c32'
            ]
            self.run_cmd(['dpkg', '-x', filename, destdir])
            for syslinux_file in syslinux_files:
                shutil.copyfile(
                    os.path.join(destdir, "usr/lib/syslinux/modules/bios/%s" % syslinux_file),
                    "%s/%s" % (cdroot, syslinux_file))
            shutil.copyfile(
                os.path.join(destdir, "usr/lib/syslinux/memdisk"),
                "%s/memdisk" % (cdroot,))
            filename = handler.download_package('isolinux', destdir)
            if filename:
                self.run_cmd(['dpkg', '-x', filename, destdir])
                shutil.copyfile(
                    os.path.join(destdir, "usr/lib/ISOLINUX/isolinux.bin"),
                    "%s/isolinux.bin" % cdroot)
            else:
                handler.clean_up_apt()
                raise Fail('Unable to download isolinux')
            handler.clean_up_apt()

            cfg = self.generate_cfg(bootconfig)
            with open("%s/%s" % (cdroot, "menu.cfg"), "w") as cfgout:
                cfgout.write(cfg)

            if bootconfig.timeout is not None:
                isolinux_cfg = os.path.join(cdroot, "isolinux.cfg")
                with open(isolinux_cfg, "rt") as fd:
                    cfg = fd.read()
                cfg1 = re.sub(r"timeout\s+\d+", "timeout {}".format(bootconfig.timeout * 10), cfg, flags=re.IGNORECASE)
                if cfg1 == cfg:
                    cfg1 = cfg + "\ntimeout {}\n".format(bootconfig.timeout * 10)
                with open(isolinux_cfg, "wt") as fd:
                    fd.write(cfg1)

            # Fix the menu display size in stdmeny.cfg (#861421)
            self.run_cmd(['sed', '-i', 's,menu rows 12,menu rows 8,g',
                          os.path.join(cdroot, 'stdmenu.cfg')])
