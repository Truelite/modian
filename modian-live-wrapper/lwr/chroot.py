import os
import shlex
import shutil
from .component import Component
from .debootstrap import Debootstrap
from .ansible import Ansible


class Chroot(Component):
    ansible_playbook = shutil.which("ansible-playbook")

    def __init__(self, sysdesc):
        super().__init__()
        self.sysdesc = sysdesc

    def build(self, dest):
        if os.path.isdir(os.path.join(dest, "etc")):
            self.log.info("%s already exists: reusing it", dest)
            return

        with self.sysdesc.cache(dest, "chroot", self.sysdesc.cache_id_chroot) as cache:
            if not cache.hit:
                debootstrap = Debootstrap(self.sysdesc)
                debootstrap.build(dest)
                # self.remove_udev_persistent_rules(dest)  # FIXME: is this needed?
                self.run_ansible(self.sysdesc, dest)
            else:
                if self.run_ansible(self.sysdesc, dest):
                    # Run cache.store() only if ansible changed anything
                    cache.store()
                else:
                    self.log.info("Ansible did not change anything: keep previous cache")

        self.update_initramfs(dest)
        self.set_target_apt_mirror(dest)
        self.enable_networkd(dest)

    def run_ansible(self, sysdesc, dest):
        """
        Run ansible and return True if it changed something
        """
        self.log.info("Customizing %s with %s", dest, sysdesc.playbook)
        vars = sysdesc.to_dict(exclude=("cache_dir", "packages"))

        with self.work_dir(self.sysdesc.ansible_dir) as workdir:
            ansible_inventory = os.path.join(workdir, "inventory.ini")
            with open(ansible_inventory, "wt") as fd:
                print("[live]", file=fd)
                print("{} ansible_connection=chroot {}".format(
                        os.path.abspath(dest),
                        " ".join("{}={}".format(k, v) for k, v in vars.items())),
                      file=fd)

            ansible_cfg = os.path.join(workdir, "ansible.cfg")
            with open(ansible_cfg, "wt") as fd:
                print("[defaults]", file=fd)
                print("nocows = 1", file=fd)
                print("inventory = {}".format(os.path.abspath(ansible_inventory)), file=fd)

            args = [self.ansible_playbook, "-v", os.path.abspath(sysdesc.playbook)]
            ansible_sh = os.path.join(workdir, "ansible.sh")
            with open(ansible_sh, "wt") as fd:
                print("#!/bin/sh", file=fd)
                print("set -xue", file=fd)
                print("export ANSIBLE_CONFIG={}".format(shlex.quote(ansible_cfg)), file=fd)
                print(" ".join(shlex.quote(x) for x in args), file=fd)
            os.chmod(ansible_sh, 0o755)

            res = self._run_ansible([ansible_sh])
            if res.result != 0:
                self.log.warn("Rerunning ansible to check what fails")
                self._run_ansible([ansible_sh])
                raise RuntimeError("ansible exited with result {}".format(res.result))
            else:
                return res.changed == 0 and res.unreachable == 0 and self.failed == 0

    def _run_ansible(self, cmd):
        ansible = Ansible()
        ansible.run_pretty(cmd)
        return ansible

    def remove_udev_persistent_rules(self, dest):
        self.log.info('Removing udev persistent cd and net rules')
        for rule in '70-persistent-cd.rules', '70-persistent-net.rules':
            pathname = os.path.join(dest, 'etc', 'udev', 'rules.d', rule)
            if os.path.exists(pathname):
                self.log.debug('Removing %s', pathname)
                os.remove(pathname)
            else:
                self.log.debug('Not removing non-existent %s', pathname)

    def update_initramfs(self, dest):
        cmd = os.path.join('usr', 'sbin', 'update-initramfs')
        if os.path.exists(os.path.join(dest, cmd)):
            self.log.info("Updating the initramfs")
            self.run_cmd(['chroot', dest, cmd, '-u'])

    def copy_files(self, src, dest):
        """
        Copy all files in src to dest
        """
        for filename in os.listdir(src):
            src_path = os.path.join(src, filename)
            if os.path.isdir(src_path) or os.path.islink(src_path):
                continue
            shutil.copyfile(
                src_path,
                os.path.join(dest, filename))

    def set_target_apt_mirror(self, dest):
        """
        Update the apt mirrors in the chroot to point to what is desired in the
        installed system. After this is run, apt is likely to stop working
        inside the chroot.

        By convention, all repositories whose configuration file name starts
        with 'inst-' are removed at this step
        """
        aptconf = os.path.join(dest, "etc", "apt")

        # Remove sources.list, leaving only the sources.list.d/ configuration
        # files
        aptconf_sourceslist = os.path.join(aptconf, "sources.list")
        if os.path.exists(aptconf_sourceslist):
            os.unlink(aptconf_sourceslist)

        # Remove repositories added for install time usage only
        aptconf_sourceslistd = os.path.join(aptconf, "sources.list.d")
        for name in os.listdir(aptconf_sourceslistd):
            if name.startswith("inst-"):
                os.unlink(os.path.join(aptconf_sourceslistd, name))

        # Add the final mirror
        with open(os.path.join(aptconf_sourceslistd, "base.list"), "wt") as fd:
            print("deb {} {} {}".format(self.sysdesc.installed_mirror, self.sysdesc.distribution, self.sysdesc.installed_mirror_components), file=fd)

        # This may fail if the installed mirrors are not accessible, and it is ok
        self.run_cmd(['chroot', dest, 'apt-get', 'update'], check=False)
        self.run_cmd(['chroot', dest, 'apt-get', 'clean'])

    def enable_networkd(self, dest):
        """
        Enable networkd and resolved.

        This needs to be run just before squashfs generation, because the
        resolv.conf breaks apt's network access unless resolved is running, and
        resolved is not running inside the chroot.

        Also, due to #895550, systemctl enable cannot currently be done via
        ansible.
        """
        self.run_cmd(["chroot", dest, "systemctl", "enable", "systemd-networkd"])
        self.run_cmd(["chroot", dest, "systemctl", "enable", "systemd-resolved"])
        resolvconf = os.path.join(dest, "etc", "resolv.conf")
        if os.path.exists(resolvconf):
            os.unlink(resolvconf)
        # delegate resonv.conf to resolved
        os.symlink("/run/systemd/resolve/resolv.conf", resolvconf)
