import re
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
        self.ok = None
        self.changed = None
        self.unreachable = None
        self.failed = None

    def run(self, cmd):
        res = self.popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
        task_name = None
        expect_recap = False
        re_task = re.compile(r"^TASK \[(?P<name>[^]]+)\]")
        re_result = re.compile(r"^(?P<status>[^:]+): (?P<host>[^]]+)\](?:: FAILED!)?(?: => (?P<json>.+))?")
        re_recap = re.compile(r"^(?P<host>.+?)\s*:\s+ok=(?P<ok>\d+)\s+changed=(?P<changed>\d+)\s+unreachable=(?P<unreachable>\d+)\s+failed=(?P<failed>\d+)")

        # Using ``line in res.stdout`` the stdout is split in too many
        # places and becomes unparseable.
        for line in res.stdout.readlines():
            if line and line[0].isspace():
                continue
            line = line.strip()
            if not line:
                continue
            if line.startswith("Using "):
                continue
            if line.startswith("PLAY RECAP "):
                expect_recap = True
                continue
            if line.startswith("PLAY "):
                continue
            mo = re_task.match(line)
            if mo:
                task_name = mo.group("name")
                self.log.info("task: %s", task_name)
                continue
            if expect_recap:
                mo = re_recap.match(line)
                if mo:
                    self.ok = mo.group("ok")
                    self.changed = mo.group("changed")
                    self.unreachable = mo.group("unreachable")
                    self.failed = mo.group("failed")
                else:
                    self.log.warn("Unparsed line in ansible output: %r", line)
            else:
                mo = re_result.match(line)
                if mo:
                    data = mo.group("json")
                    if data:
                        data = json.loads(data)
                    yield TaskOutcome(mo.group("host"), task_name, mo.group("status"), data)
                else:
                    self.log.warn("Unparsed line in ansible output: %r", line)

        self.result = res.wait()

    def run_pretty(self, cmd):
        for to in self.run(cmd):
            if to.status == "ok":
                self.log.info("%s: %s", to.name, to.status)
            else:
                self.log.warn("%s: %s", to.name, to.status)
                if to.data:
                    stdout = to.data.pop("stdout", None)
                    if stdout:
                        for line in stdout.splitlines():
                            self.log.info("out: %s", line)
                    stderr = to.data.pop("stderr", None)
                    if stderr:
                        for line in stderr.splitlines():
                            self.log.warn("err: %s", line)
                    to.data.pop("stdout_lines", None)
                    to.data.pop("stderr_lines", None)
                    self.log.warn("other task data: %s", json.dumps(to.data))
