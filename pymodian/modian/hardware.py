from __future__ import annotations

import logging
import os
import re
import shlex
import subprocess
from typing import Dict, Generator, List, Optional, Tuple

from .exceptions import ModianError
from .config import Config

log = logging.getLogger()


class Hardware:
    """
    Hardware detection and operations
    """

    def __init__(self, env_config: Config):
        self.env_config = env_config
        # Check if we are on a UEFI system
        self.uefi = False
        try:
            res = subprocess.run(['efibootmgr'],
                                 capture_output=True, check=False)
            if res.returncode == 0:
                self.uefi = True
        except FileNotFoundError:
            pass

    def _read_sys_file(self, dev: str) -> str:
        with open(dev, "rt") as fd:
            return fd.read().strip()

    def run_cmd_stop_errors(self, cmd: List[str], *args, **kw) \
            -> subprocess.CompletedProcess:
        """
        Run a command with subprocess and stop in case of errors
        """
        res = subprocess.run(cmd, *args, **kw)
        if res.returncode != 0:
            fcmd = " ".join(shlex.quote(c) for c in cmd)
            raise ModianError(
                f"Command ``{fcmd}`` failed, returncode is {res.returncode}"
            )
        return res

    def read_iso_volume_id(self, pathname: str) -> str:
        with open(pathname, "rb") as fd:
            fd.seek(0x8028)
            return fd.read(32).decode("utf-8").strip()

    def get_live_media_device(self) -> Optional[str]:
        live_media_re = re.compile(
            r"^/dev/(?P<dev>\S+) /run/live/medium iso9660"
        )
        with open("/proc/mounts", "rt") as fd:
            for line in fd:
                mo = live_media_re.match(line)
                if mo:
                    devname = mo.group("dev")
                    # the live media device can be a full device or a
                    # partition; either way we select the relevant block
                    # device from /sys/block/
                    for b_dev in os.listdir('/sys/block/'):
                        if devname.startswith(b_dev):
                            return b_dev
        return None

    def size(self, devname: str) -> int:
        return int(self._read_sys_file("/sys/block/{}/size".format(devname)))

    def desc(self, devname: str) -> str:
        return self._read_sys_file(
            "/sys/block/{}/device/model".format(devname)
        )

    def list_devices(self) -> Generator[str, None, None]:
        for name in os.listdir("/sys/block"):
            # sd* sata disk
            # nvme* NVM express disk
            if not name.startswith("sd") and not name.startswith("nvme"):
                continue
            yield name

    def list_partition_labels(self) -> Generator[Tuple[str, str], None, None]:
        for name in os.listdir("/dev/disk/by-label"):
            dest = os.path.abspath(
                os.readlink(os.path.join("/dev/disk/by-label", name))
            )
            yield name, os.path.basename(dest)

    def get_uefi_partition(self, name: str) -> Optional[str]:
        import parted

        pdev = parted.getDevice("/dev/" + name)
        try:
            pdisk = parted.newDisk(pdev)
        except parted.DiskException as e:
            if "unrecognised disk label" in e.args[0]:
                return None
            else:
                raise

        if pdisk.type != "gpt":
            log.error(
                "device %s has partition table type %s instead of gpt",
                name,
                pdisk.type,
            )
            return None
        for part in pdisk.partitions:
            if part.getFlag(18):
                log.info("Found ESP partition in %s", part.path)
                return os.path.basename(part.path)
        log.info("No ESP partition found in %s", name)
        return None

    def get_GiB_disk_size(self, disk: str) -> int:
        """
        return the disk size in GiB
        """
        res = self.run_cmd_stop_errors(
            ["lsblk", "--noheadings", "--nodeps", "--bytes",
             "--output", "SIZE", disk],
            capture_output=True, text=True)
        return int(res.stdout) / (1_000_000_000)

    def get_disk_model(self, disk: str) -> str:
        """
        return the model of the disk

        """
        model_fname = os.path.join("/sys/block", disk, "device/model")
        with open(model_fname) as fp:
            model = fp.read()
        return model.strip()

    def create_mtab(self):
        """
        Create an mtab if it doesn't exist.
        """
        log.info("Creating mtab")
        if not os.path.exists('/etc/mtab'):
            os.symlink('/proc/mounts', '/etc/mtab')

    def disable_swap(self):
        """
        Disable any swap partition.
        """
        log.info("Disabling swap")
        self.run_cmd_stop_errors(["swapoff", "-a"])

    def get_partition_disk_name(self, disk: str, number: int) -> str:
        """
        Get the device name of the partition <number> on <disk>
        """
        device_name = disk.strip("/dev/")
        if device_name.startswith("sd"):
            # sata disk: the partition number is simply appended
            return f"{disk}{number}"
        elif device_name.startswith("nvme"):
            # nvme disk: there is a p between the name of the disk and
            # the partition number
            return f"{disk}p{number}"
        else:
            raise ModianError(f"Unsupported disk type {disk}")

    def get_partition_recipe_fname(self, device: str, recipe: str) -> str:
        """
        Get the filename of an appropriate parted recipe.

        This can be overridden to add custom checks on the size or any
        other known property of the device.

        Return a string with the full path of the recipe.
        """
        disksizeGiB = self.get_GiB_disk_size(device)

        # TODO: The current -32G parted file looks like it's supposed to
        # partition disks larger than 32GiB. However, this check maintains
        # compatibility with the previous shell code: it could be that one of
        # the paths was not tested, and that, after investigation, this check
        # might not be needed anymore
        if disksizeGiB < 32:
            recipe_fname = "{}-32G.parted"
        else:
            recipe_fname = "{}.parted"

        recipe_fname = recipe_fname.format(recipe)

        if not recipe_fname.endswith(".parted"):
            recipe_fname = recipe_fname + ".parted"

        partition_table_recipe = os.path.join(
            "/etc/modian/partitions/"
            recipe_fname.format(recipe)
        )

        return partition_table_recipe

    def partition_disk(self, device: str, recipe: str):
        """
        Partition the disk using the parted script with the given name.
        """
        # wipe MBR
        self.run_cmd_stop_errors([
            "sgdisk", "--zap-all", device
        ])
        self.run_cmd_stop_errors([
            "dd",
            "if=/dev/zero",
            'of={}'.format(device),
            "bs=446",
            "count=1",
            "status=none",
        ])
        partition_table_recipe = self.get_partition_recipe_fname(
            device, recipe
        )

        log.info("Partitioning disk %s", device)

        with open(partition_table_recipe, "r") as fp:
            for line in fp:
                if line:
                    self.run_cmd_stop_errors([
                        "parted",
                        "-s",
                        "-a", "optimal",
                        device,
                        "--",
                        *line.split(),
                    ])

        self.run_cmd_stop_errors(["partx", "-u", device])
        self.run_cmd_stop_errors(["partx", "-s", device])

    def format_device(self, label: str, device: str):
        """
        Format a device (e.g. /dev/sda1) with a label.
        """
        log.info("%s: setting up %s partition", device, label)
        # If the partition is mounted we try to umount it; if it fails
        # because the partition wasn't mounted it's ok, for any other
        # error mkfs will refuse to work anyway.
        subprocess.run(["umount", device], check=False)
        self.run_cmd_stop_errors([
            "mkfs.ext4", "-q", "-F", "-L", label, device
        ])
        self.run_cmd_stop_errors(["tune2fs", "-c", "0", "-i", "1m", device])


class Blockdev:
    """
    Information for a block device
    """

    def __init__(self, hardware: Hardware, name: str):
        # device name without /dev
        self.name = name
        # Size in 512 byte blocks
        self.size = hardware.size(name)
        # Description
        self.desc = hardware.desc(name)

    @property
    def device(self) -> str:
        return "/dev/{}".format(self.name)

    def __str__(self):
        return self.name

    @property
    def details(self) -> str:
        return "{:,}GB, {}".format(
            int(self.size * 512 / (1_000_000_000)), self.desc
        )

    @classmethod
    def list(cls, hardware: Hardware) -> Generator["Blockdev", None, None]:
        """
        List all sd* or nvme block devices, generating a sequence of
        Blockdev objects.
        """
        for name in hardware.list_devices():
            bd = cls(hardware, name)
            log.debug("found device %s (%s)", bd.name, bd.details)
            yield bd


class Partition:
    """
    Information about a partition
    """
    def __init__(self, disk: Blockdev, dev: str, label: str):
        self.disk = disk
        self.dev = dev
        self.label = label

    def __str__(self):
        return self.dev


class System:
    LABELS = {
        "root": "##root##",
        "log": "##log##",
        # Not really a disk label, but used to identify ESP partition
        "esp": "##ESP##",
    }

    def __init__(self, hardware: Hardware):
        self.hardware = hardware
        self.blockdevs: Dict[str, Blockdev] = {
            x.name: x for x in Blockdev.list(hardware)}
        self.labels: Dict[str, str] = dict(
            self.hardware.list_partition_labels())
        self._disk_inst: Optional[Blockdev] = None
        self._disk_root: Optional[Blockdev] = None
        # Partitions indexed by label
        self.partitions: Dict[str, Partition] = {}

    @property
    def disk_inst(self) -> Blockdev:
        if self._disk_inst is None:
            raise ModianError("installation disk not detected")
        else:
            return self._disk_inst

    @property
    def disk_root(self) -> Blockdev:
        if self._disk_root is None:
            raise ModianError("root disk not detected")
        else:
            return self._disk_root

    def _check_partition(self, label: str, disk: Blockdev) -> bool:
        """
        Check that a partition with the given label exists on the given disk,
        and if it does, add it to self.partitions
        """
        dev = self.labels.get(label, None)
        if dev is None:
            log.debug("label %s not found", label)
            return True
        # remove the last char (partition number), example sda1 --> sda
        disk_name = dev.rstrip("0123456789")
        # if there is nvm disk i have to remove also p char at the end,
        # example nvme1n1p1 --> nvme1n1 (doesn't exits sdp!!!)
        disk_name = disk_name.rstrip("p")
        log.debug("found %s for %s on disk %s", dev, label, disk_name)
        if disk_name != disk.name:
            log.error(
                "label %s found on disk %s instead of %s",
                label,
                disk_name,
                disk.name,
            )
            return False

        part = Partition(disk, dev, label)
        self.partitions[label] = part
        return True

    def _check_uefi_partition(self, disk: Blockdev) -> bool:
        """
        Check that a UEFI partition exists, and if it does, add it to
        self.partitions
        """
        dev = self.hardware.get_uefi_partition(disk.name)
        if dev is None:
            return True
        part = Partition(disk, dev, self.LABELS["esp"])
        self.partitions[self.LABELS["esp"]] = part
        return True

    def read_additional_partition_labels(self) -> bool:
        """
        Override this method to check for additional partitions.
        """
        return True

    def _read_partition_labels(self):
        ok = True
        ok = self._check_partition(self.LABELS["root"], self.disk_root) and ok
        ok = self._check_partition(self.LABELS["log"], self.disk_root) and ok
        if self.hardware.uefi:
            ok = self._check_uefi_partition(self.disk_root) and ok
        ok = self.read_additional_partition_labels() and ok
        if not ok:
            raise ModianError(
                "inconsistencies found with existing disk partitions"
            )

    def select_disks(self) -> Tuple[bool, List[Blockdev]]:
        """
        Select which disk should be used for root or other partitions.

        Returns True if the selection was succesful, False if a
        selection could not be made.

        The default is to select the smallest disk for root; you can
        extend this method to select further disks, or override it
        completely to use a different selection method.
        """
        live_media_dev_name = self.hardware.get_live_media_device()
        if live_media_dev_name is None:
            log.error("cannot found live media device mounted in /proc/mounts")
            ok = False

        devs: List[Blockdev] = []
        for bd in self.blockdevs.values():
            if bd.name == live_media_dev_name:
                self._disk_inst = bd
                continue
            devs.append(bd)

        ok = True
        if self._disk_inst is None:
            log.error(
                "live install media device %r not found", live_media_dev_name
            )
            ok = False
            return ok, []

        if len(devs) == 0:
            log.info("No disk found")
            ok = False
        elif len(devs) == 1:
            log.info(
                "selected the only disk %s as the root device", devs[0].name
            )
            self._disk_root = devs[0]
        else:
            # Try selecting the image device as the biggest one
            devs.sort(key=lambda x: x.size)
            if devs[0].size == devs[1].size:
                devs.sort(key=lambda x: x.name)
                self._disk_root = devs[0]
                log.info(
                    "Selected %s as root, as the first name of the two",
                    self._disk_root,
                )
            else:
                self._disk_root = devs[0]
                log.info(
                    "Selected %s as root, as the smallest of two",
                    self._disk_root,
                )
        return ok, devs

    def log_found_devices(self):
        """
        Log all devices and partitions that have been found.

        Override this to list the additional devices and partitions that
        your derived installer is expecting.
        """
        log.info(
            "Root device: %s (%s)", self.disk_root.name, self.disk_root.details
        )
        log.info(
            "Installation media: %s (%s)",
            self.disk_inst.name,
            self.disk_inst.details,
        )

        self._read_partition_labels()
        log.info(
            "Partition %s: %s",
            self.LABELS["root"],
            self.partitions.get(self.LABELS["root"], None),
        )
        log.info(
            "Partition %s: %s",
            self.LABELS["log"],
            self.partitions.get(self.LABELS["log"], None)
        )
        log.info(
            "Partition %s: %s",
            self.LABELS["esp"],
            self.partitions.get(self.LABELS["esp"], None)
        )

    def detect(self, uefi=False):
        ok = True

        ok, devs = self.select_disks()

        if not ok:
            raise ModianError("disk detection failed")

        self.log_found_devices()

    def compute_firstinstall_actions(self) -> List[str]:
        actions = [
            "clean_lvm_groups",
            "setup_disk_root",
            "setup_disk_images",
        ]
        return actions

    def check_additional_root_disk_partitions(self) -> List[str]:
        """
        Return a list of extra partition labels currently missing from the root
        disk
        """
        return []

    def compute_additional_root_disk_partition_actions(self) -> List[str]:
        return []

    def compute_additional_disks_actions(self) -> List[str]:
        return []

    def compute_actions(self) -> List[str]:
        actions: List[str] = []

        # If the iso image volume name is "firstinstall", then we always run a
        # first install
        iso_volume_id = self.hardware.read_iso_volume_id(
            self.disk_inst.device)
        log.debug("ISO volume id is '%s'", iso_volume_id)
        if iso_volume_id == "firstinstall":
            log.info(
                "running a firstinstall key: "
                + "force complete reinstall of the machine"
            )
            actions.extend(self.compute_firstinstall_actions())
        else:
            # Check whether the mandatory partitions exist
            missing = []
            if self.LABELS["root"] not in self.partitions:
                missing.append(self.LABELS["root"])
            if self.LABELS["log"] not in self.partitions:
                missing.append(self.LABELS["log"])
            if self.hardware.uefi \
                    and self.LABELS["esp"] not in self.partitions:
                missing.append(self.LABELS["esp"])

            missing.extend(self.check_additional_root_disk_partitions())

            actions.append("clean_lvm_groups")
            if not missing:
                log.info("all partitions found in root disk")
                # formatting / installing root and log
                # leaving data intact
                actions.append("format_part_root")
                actions.append("format_part_log")
                if self.hardware.uefi:
                    actions.append("format_part_esp")
                    actions.extend(
                        self.compute_additional_root_disk_partition_actions()
                    )
            else:
                log.info(
                    "partition(s) %s not found in root disk", " ".join(missing)
                )
                # first install of the root disk
                actions.append("setup_disk_root")

            actions.extend(self.compute_additional_disks_actions())

        log.info("computed actions: %s", " ".join(actions))

        return actions

    def umount_partitions_target_drives(self) -> List[str]:
        """
        Umount all partitions from the target drives.

        Return the list of remaining mounts, for convenience when
        overriding the method.
        """
        with open('/proc/mounts') as fp:
            mounts = fp.readlines()
        if self.disk_root is not None:
            for line in mounts:
                if self.disk_root.name in line:
                    subprocess.run(["umount", line.split()[0]], check=False)
                    mounts.remove(line)

        return mounts
