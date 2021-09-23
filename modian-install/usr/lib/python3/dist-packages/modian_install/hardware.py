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

    def _read_sys_file(self, dev):
        with open(dev, "rt") as fd:
            return fd.read().strip()

    def read_iso_volume_id(self, pathname):
        with open(pathname, "rb") as fd:
            fd.seek(0x8028)
            return fd.read(32).decode("utf-8").strip()

    def get_live_media_device(self):
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

    def size(self, devname):
        return int(self._read_sys_file("/sys/block/{}/size".format(devname)))

    def desc(self, devname):
        return self._read_sys_file(
            "/sys/block/{}/device/model".format(devname)
        )

    def list_devices(self):
        for name in os.listdir("/sys/block"):
            # sd* sata disk
            # nvme* NVM express disk
            if not name.startswith("sd") and not name.startswith("nvme"):
                continue
            yield name

    def list_partition_labels(self):
        for name in os.listdir("/dev/disk/by-label"):
            dest = os.path.abspath(
                os.readlink(os.path.join("/dev/disk/by-label", name))
            )
            yield name, os.path.basename(dest)

    def get_uefi_partition(self, name):
        import parted

        pdev = parted.getDevice("/dev/" + name)
        pdisk = parted.newDisk(pdev)
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

    def get_GiB_disk_size(self, disk):
        """
        return the disk size in GiB
        """
        fdisk_res = subprocess.run(
            ["fdisk", "-l"],
            capture_output=True
        )
        for line in fdisk_res.stdout.split(b'\n'):
            if line.startswith("Disk {}".format(disk)):
                return int(line.split()[2].split(".")[0])
