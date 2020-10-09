"""
  Wrapper for distro information
"""
# -*- coding: utf-8 -*-
#
#  codenames.py
#
#  Copyright 2015 Neil Williams <codehelp@debian.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import datetime
from distro_info import DebianDistroInfo


class Codenames:
    """
    Compute kernel package name from distribution and architecture
    """
    def __init__(self, distribution):
        super(Codenames, self).__init__()
        self.distribution = distribution
        self.debian_info = DebianDistroInfo()

    def suite_to_codename(self, distro):
        suite = self.debian_info.codename(distro, datetime.date.today())
        if not suite:
            return distro
        return suite

    def was_oldstable(self, limit):
        suite = self.suite_to_codename(self.distribution)
        # this check is only for debian
        if not self.debian_info.valid(suite):
            return False
        return suite == self.debian_info.old(limit)

    def was_stable(self, limit):
        suite = self.suite_to_codename(self.distribution)
        # this check is only for debian
        if not self.debian_info.valid(suite):
            return False
        return suite == self.debian_info.stable(limit)

    def kernel_package(self, arch):
        if arch == 'i386':
            # wheezy (which became oldstable on 2015-04-25) used '486'
            if self.was_oldstable(datetime.date(2015, 4, 26)):
                kernel_arch = '486'
            # jessie (which became oldstable on 2017-06-17) used '586'
            elif self.was_oldstable(datetime.date(2017, 6, 18)):
                kernel_arch = '586'
            else:
                kernel_arch = '686'
        elif arch == 'armhf':
            kernel_arch = 'armmp'
        elif arch == 'ppc64el':
            kernel_arch = 'powerpc64le'
        else:
            kernel_arch = arch
        return 'linux-image-' + kernel_arch
