from __future__ import annotations
import os
import shlex
import shutil
import subprocess
import tempfile
import contextlib
import logging


class Component:
    """
    Common functions for live-wrapper components
    """
    eatmydata = shutil.which("eatmydata")

    def __init__(self):
        name = getattr(self, "name", None)
        if name is None:
            self.name = self.__class__.__name__.lower()
        self.log = logging.getLogger(self.name)

    def run_cmd(self, args, check=True, eatmydata=True, **kw):
        if eatmydata and self.eatmydata:
            args = [self.eatmydata] + args
        self.log.debug("run: %s", " ".join(shlex.quote(x) for x in args))
        return subprocess.run(args, check=check, **kw)

    def popen(self, args, eatmydata=True, **kw):
        if eatmydata and self.eatmydata:
            args = [self.eatmydata] + args
        self.log.debug("run: %s", " ".join(shlex.quote(x) for x in args))
        return subprocess.Popen(args, **kw)

    @contextlib.contextmanager
    def work_dir(self, existing=None):
        """
        Create a temporary directory, or reuse an existing one
        """
        if existing:
            os.makedirs(existing, exist_ok=True)
            yield existing
        else:
            with tempfile.TemporaryDirectory() as work_dir:
                yield work_dir

    @contextlib.contextmanager
    def work_file(self, name, existing=None, mode="w+b", reuse=False):
        """
        Create a temporary file, or a file in the existing work directory
        """
        if existing:
            os.makedirs(existing, exist_ok=True)
            pathname = os.path.join(existing, name)
            if reuse and os.path.exists(pathname):
                with open(pathname, mode=mode.replace("w", "r")) as file:
                    yield file
            else:
                with open(pathname, mode=mode) as file:
                    yield file
        else:
            with tempfile.NamedTemporaryFile(mode=mode) as file:
                yield file
