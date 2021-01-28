from __future__ import annotations
import subprocess
import json
from .component import Component


class TaskOutcome:
    def __init__(self, host, name, status, data):
        self.host = host
        self.name = name
        self.status = status
        self.data = data


class Ansible(Component):
    def __init__(self):
        super().__init__()
        self.result = None
        self.ok = 0
        self.changed = 0
        self.unreachable = 0
        self.failed = 0

    def run(self, cmd):
        res = self.popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

        # Some parts of Ansible may sadly print warnings on stdout (instead of
        # stderr!) before the JSON output, so we are preprocessing stdout to
        # skim those warnings out
        stdout, stderr = res.communicate()
        stdout_lines = stdout.splitlines()
        while stdout_lines and stdout_lines[0] != "{":
            self.log.warn("ansible remarks: %s", stdout_lines.pop(0))
        stdout = "\n".join(stdout_lines)

        if stdout:
            results = json.loads(stdout)
            for stats in results["stats"].values():
                self.ok += stats["ok"]
                self.changed += stats["changed"]
                self.unreachable += stats["unreachable"]
                self.failed += stats["failures"]

            for play in results["plays"]:
                for task in play["tasks"]:
                    for host, result in task["hosts"].items():
                        status = "ok"
                        if result.get("failed"):
                            status = "failed"
                        yield TaskOutcome(host, task["task"]["name"], status, result)
        else:
            self.log.warn("Ansible failed to start:")
            self.log.warn(stderr)
            yield TaskOutcome("", "", "failed", {'result': 'failed'})

        self.result = res.wait()

    def run_pretty(self, cmd):
        for to in self.run(cmd):
            if to.status == "ok":
                self.log.info("%s: %s", to.name, to.status)
            else:
                self.log.warn("%s: %s", to.name, to.status)
                if to.data:
                    stdout = to.data.get("stdout")
                    if stdout:
                        for line in stdout.splitlines():
                            self.log.info("out: %s", line)
                    stderr = to.data.get("stderr")
                    if stderr:
                        for line in stderr.splitlines():
                            self.log.warn("err: %s", line)
                    to.data.pop("stdout_lines", None)
                    to.data.pop("stderr_lines", None)
                    self.log.warn("other task data: %s", json.dumps(to.data))
