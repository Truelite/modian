# live-wrapper - Wrapper for vmdebootstrap for creating live images
# (C) Iain R. Learmonth 2015 <irl@debian.org>
# See COPYING for terms of usage, modification and redistribution.
#
# lwr/cdroot.py - cdroot helpers

import os
import shutil
import tempfile


class CDRoot(object):
    def __init__(self, path=None):
        if not path:
            self.path = tempfile.mkdtemp()
            self.delete = True
        else:
            self.path = path
            os.makedirs(path, exist_ok=True)
            self.delete = False

    def __getitem__(self, i):
        return CDRoot(os.path.join(self.path, i))

    def __str__(self):
        return self.path

    def __del__(self):
        if self.delete:
            shutil.rmtree(self.path)
