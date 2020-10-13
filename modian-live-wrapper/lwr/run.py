# live-wrapper - Wrapper for vmdebootstrap for creating live images
# (C) Iain R. Learmonth 2015 <irl@debian.org>
# See COPYING for terms of usage, modification and redistribution.
#
# lwr/run.py - Live Wrapper (Application)

"""
This script is the main script for the live-wrapper application. It is
intended to be run from the command line.

See live-wrapper(8) for more information.
"""

import sys
import os
import argparse
import logging
import pycurl
import shutil
import subprocess
from tarfile import TarFile
from lwr.isolinux import Isolinux
from lwr.bootloader import BootloaderConfig
from lwr.disk import install_disk_info, get_default_description
from lwr.grub import install_grub
from lwr.xorriso import Xorriso
from lwr.apt_udeb import AptUdebDownloader, get_apt_handler
from lwr.utils import cdrom_image_url, KERNEL, RAMDISK, Fail
from lwr.cdroot import CDRoot
from lwr.base_system import BaseSystem
from lwr.component import Component
from lwr.codenames import Codenames

__version__ = '0.7'


def run_vmdebootstrap(args, dest):
    # TODO: "hostname": "debian",
    packages = []
    packages.extend(args.tasks.split())
    packages.extend(args.extra.split())
    packages.extend(args.firmware.split())
    packages.extend(args.base_debs.split())

    kernel_package = Codenames(args.distribution).kernel_package(args.architecture)
    if not args.no_auto_kernel:
        packages.append(kernel_package)

    base_system_args = {
        "distribution": args.distribution,
        "architecture": args.architecture,
        "build_mirror": args.mirror,
        "installed_mirror": args.apt_mirror,
        "installed_mirror_components": args.apt_mirror_components,
        "playbook": args.playbook,
        "networkd": args.networkd,
        "cache_dir": args.cache_dir,
        "customize_squashfs": args.customize_squashfs,
        "squashfs_compression": args.squashfs_comp,
        "packages": packages,
        "kernel_package": kernel_package,
    }

    if args.work_dir:
        base_system_args["chroot_dir"] = os.path.join(args.work_dir, "chroot")
        base_system_args["ansible_dir"] = os.path.join(args.work_dir, "ansible")
    sysdesc = BaseSystem(**base_system_args)
    sysdesc.build(dest)


class LiveWrapper(Component):

    # Instance variables
    cdroot = None  # The path to the chroot the CD is being built in
    kernel_path = None
    ramdisk_path = None
    gtk_kernel_path = None
    gtk_ramdisk_path = None

    def __init__(self, version=__version__):
        super().__init__()
        self.version = version

    def add_settings(self, parser):
        default_arch = subprocess.check_output(["dpkg", "--print-architecture"], universal_newlines=True).strip()
        distro = parser.add_argument_group(title="Distribution Settings")
        distro.add_argument("--distribution", "-d", action="store", metavar="NAME", default="buster",
                            help='Debian release to use')
        distro.add_argument("--architecture", action="store", metavar="ARCH", default=default_arch,
                            help='architecture to use')
        distro.add_argument("--apt-mirror", action="store", metavar="mirror_url", default="http://deb.debian.org/debian/",
                            help='Mirror to configure in the built image')
        distro.add_argument("--apt-mirror-components", action="store", metavar="main [contrib [..]]", default="main",
                            help='Components to activate in the built image apt configuration')
        distro.add_argument("--playbook", action="store", metavar="file.yaml", default="chroot.yaml",
                            help='Ansible playbook to run to customize the system')
        distro.add_argument("--networkd", action="store_true",
                            help='Enable systemd-networkd and systemd-resolved')
        distro.add_argument("--tasks", "-t", action="store", metavar='"task-TASK1 task-TASK2 ..."', default="",
                            help='Task packages to install')
        distro.add_argument("--extra", "-e", action="store", metavar='"PKG1 PKG2 ..."', default="",
                            help='Extra packages to install')
        distro.add_argument("--firmware", "-f", action="store", metavar='"PKG1 PKG2 ..."', default="",
                            help='Firmware packages to install')
        distro.add_argument("--customize-squashfs", action="store", metavar="script.sh", default=None,
                            help="If set, run this script with the chroot path as argument before running mksquashfs")
        distro.add_argument("--no-auto-kernel", action="store_true",
                            help="Do not automatically install a kernel in the chroot. When using this option,"
                                 " it is assumed that the ansible playbook takes care of installing a kernel")

        base = parser.add_argument_group(title="Base Settings")
        base.add_argument("--image-output", "-o", action="store", metavar="file.iso", default="live.iso",
                          help="Location for built image")
        base.add_argument("--mirror", "-m", action="store", metavar="mirror_url", default="http://deb.debian.org/debian/",
                          help='Mirror to use for image creation')
        base.add_argument("--cache-dir", action="store", metavar="path", default=None,
                          help='If set, cache intermediate data in this directory')
        base.add_argument("--work-dir", action="store", metavar="path", default=None,
                          help="If set, work in this directory instead of a temporary directory")
        base.add_argument("--retry", action="store_true",
                          help="Keep the existing work dir, and skip steps for which output already exists")

        iso = parser.add_argument_group(title="ISO Settings")
        iso.add_argument("--volume-id", action="store", metavar="VOLID", default="DEBIAN LIVE",
                         help='Volume ID for the image')
        iso.add_argument("--description", action="store", metavar="DESCRIPTION", default=get_default_description(None),
                         help='Description for the image to be created. A '
                              'description will be automatically generated based '
                              'on the distribution chosen if none is specified.')
        iso.add_argument("--no-grub", action="store_false", dest="grub",
                         help='Do not add GRUB bootloader to the image (for EFI support)')
        iso.add_argument("--grub-loopback-only", action="store_true",
                         help='Only install the loopback.cfg GRUB '
                              'configuration (for loopback support) (overrides --grub)')
        iso.add_argument("--no-isolinux", action="store_false", dest="isolinux",
                         help='Do not add isolinux bootloader to the image')
        iso.add_argument("--bootappend", action="store", default=None, metavar="string",
                         help='Append this string to the kernel command line')
        iso.add_argument("--boot-timeout", action="store", type=int, metavar="seconds", default=None,
                         help='Boot timeout in seconds')
        iso.add_argument("--no-installer", action="store_false", dest="installer",
                         help='Include Debian Installer in the Live image')
        iso.add_argument("--di-daily", action="store_true",
                         help='Use the daily Debian Installer builds not releases')
        iso.add_argument("--base-debs", action="store", metavar='"PKG1 PKG2 ..."', default="",
                         help='Base packages for the installer')
        iso.add_argument("--squashfs-comp", action="store", metavar="gzip|lzo|gz", default="lzo",
                         help="Squashfs compression algorithm")
        iso.add_argument("--customize-iso", action="store", metavar="script.sh", default=None,
                         help="If set, run this script with the path to the iso contents as argument before running xorriso")

    def download_file(self, url, filehandle):
        try:
            curl = pycurl.Curl()
            curl.setopt(curl.URL, url)
            curl.setopt(curl.WRITEDATA, filehandle)
            curl.setopt(curl.FOLLOWLOCATION, True)
            curl.setopt(curl.MAXREDIRS, 8)
            curl.perform()
            curl.close()
        except pycurl.error:
            self.log.critical("Failed to fetch %s. Cannot continue!", url)
            sys.exit(1)

    def fetch_di_helpers(self, mirror, suite, architecture):
        bootdir = self.cdroot['boot'].path
        with self.work_file("di-helpers.tar.gz", self.args.work_dir, reuse=True) as ditar:
            if os.fstat(ditar.fileno()).st_size == 0:
                self.log.info("Downloading helper files from debian-installer team...")
                urls = cdrom_image_url(mirror, suite, architecture, gtk=False, daily=self.args.di_daily)
                self.download_file(urls[3], ditar)
                ditar.flush()
            else:
                self.log.info("Reusing existing helper tarball")
            info = TarFile.open(ditar.name, 'r:gz')
            if self.args.isolinux:
                isolinuxdir = self.cdroot['isolinux'].path
                isolinux_filenames = ['./isolinux.cfg', './stdmenu.cfg', './splash.png']
                isolinux_files = [f for f in info if f.name in isolinux_filenames]
                info.extractall(members=isolinux_files, path=isolinuxdir)
            if self.args.grub:
                # The act of fetching the path creates the directory
                self.log.info("Created GRUB directory at %s", self.cdroot['boot']['grub'].path)
                grub_files = [f for f in info if f.name.startswith('./grub/')]
                info.extractall(members=grub_files, path=bootdir)
            info.close()

    def fetch_di_installer(self, mirror, suite, architecture):
        self.log.info("Downloading installer files from debian-installer team...")
        if self.args.installer:
            self.log.debug("Created d-i kernel and ramdisk directory at %s", self.cdroot['d-i'].path)
            self.log.debug("Created d-i GTK kernel and ramdisk directory at %s", self.cdroot['d-i']['gtk'].path)
            self.kernel_path = os.path.join(self.cdroot['d-i'].path, KERNEL)
            self.ramdisk_path = os.path.join(self.cdroot['d-i'].path, RAMDISK)

        if self.args.installer:
            # fetch debian-installer
            urls = cdrom_image_url(mirror, suite, architecture, gtk=False, daily=self.args.di_daily)
            with open(self.kernel_path, 'w') as kernel:
                self.download_file(urls[1], kernel)
            with open(self.ramdisk_path, 'w') as ramdisk:
                self.download_file(urls[2], ramdisk)

            # Now get the graphical installer.
            urls = cdrom_image_url(mirror, suite, architecture, gtk=True, daily=self.args.di_daily)
            self.gtk_kernel_path = os.path.join(self.cdroot['d-i']['gtk'].path, KERNEL)
            self.gtk_ramdisk_path = os.path.join(self.cdroot['d-i']['gtk'].path, RAMDISK)
            with open(self.gtk_kernel_path, 'w') as kernel:
                self.download_file(urls[1], kernel)
            with open(self.gtk_ramdisk_path, 'w') as ramdisk:
                self.download_file(urls[2], ramdisk)

    def start_ops(self):  # pylint: disable=too-many-statements
        """
        This function creates the live image using the settings determined by
        the arguments passed on the command line.

        .. note::
            This function is called by process_args() once all the arguments
            have been validated.
        """

        # Create work directory
        if self.args.work_dir and os.path.isdir(self.args.work_dir):
            if not self.args.retry:
                shutil.rmtree(self.args.work_dir)
            self.cdroot = CDRoot(path=os.path.join(self.args.work_dir, "iso"))
        else:
            self.cdroot = CDRoot()
        # all other directories are based off cdroot
        self.log.debug("Created temporary work directory (cdroot) at %s.", self.cdroot.path)

        # Make options available to customise hooks
        os.environ['LWR_MIRROR'] = self.args.mirror
        os.environ['LWR_DISTRIBUTION'] = self.args.distribution
        os.environ['LWR_TASK_PACKAGES'] = self.args.tasks
        os.environ['LWR_EXTRA_PACKAGES'] = self.args.extra
        os.environ['LWR_FIRMWARE_PACKAGES'] = self.args.firmware
        os.environ['LWR_BASE_DEBS'] = self.args.base_debs

        for envvar in os.environ.keys():
            if envvar.startswith('LWR_'):
                self.log.debug("environment: %s = '%s'", envvar, os.environ[envvar])

        # Run vmdebootstrap, putting files in /live/
        if os.environ.get("LWR_DEBUG") and "skipvm" in os.environ.get('LWR_DEBUG'):
            self.log.warning("The debug option to skip running vmdebootstrap was enabled.")
            self.log.info("Creating a dummy live/ directory at %s, but not installing a live system.", self.cdroot['live'].path)
        else:
            self.log.info("Running vmdebootstrap...")
            run_vmdebootstrap(self.args, self.cdroot["live"].path)

        # Initialise menu
        # Fetch D-I helper archive
        self.fetch_di_helpers(
            self.args.mirror,
            self.args.distribution,
            self.args.architecture)

        # Fetch D-I installers if needed???
        if self.args.installer:
            print("Fetching Debian Installer")
            self.fetch_di_installer(
                self.args.mirror,
                self.args.distribution,
                self.args.architecture)

        # Download the udebs
        if self.args.installer:
            print("Downloading udebs for Debian Installer...")  # FIXME: self.message()
            self.log.info("Downloading udebs for Debian Installer...")
            # FIXME: get exclude_list from user
            exclude_list = []
            # FIXME: may need a change to the download location
            di_root = self.cdroot['d-i'].path
            apt_udeb = AptUdebDownloader(destdir=di_root)
            apt_udeb.mirror = self.args.mirror
            apt_udeb.architecture = self.args.architecture
            apt_udeb.codename = self.args.distribution
            self.log.debug("Updating local cache for %s %s...", apt_udeb.architecture, apt_udeb.codename)
            apt_udeb.prepare_apt()
            # FIXME: add support for a custom apt source on top.

            # download all udebs in the suite, except exclude_list
            apt_udeb.download_udebs(exclude_list)

            # Now we've downloaded all the d-i bits we need, clean up the metadata we used
            apt_udeb.clean_up_apt()
            print("... completed udeb downloads")
            self.log.info("... completed udeb downloads")

            # download the basic debs needed - bootloaders and tools they depend on
            if os.path.exists('base_debs.list'):
                pkg_list = []
                with open('base_debs.list', 'r') as f:
                    for line in f.readlines():
                        pkg_list.append(line.rstrip())
                di_root = self.cdroot['d-i'].path
                handler = get_apt_handler(di_root,
                                          self.args.mirror,
                                          self.args.distribution,
                                          self.args.architecture)
                handler.download_base_debs(pkg_list)
                handler.clean_up_apt()
                apt_udeb.download_base_debs(exclude_list)

                print("... completed deb downloads")
                self.log.info("... completed deb downloads")

            # Generate Packages and Release files for the udebs and downloaded debs
            apt_udeb.generate_packages_file('udeb')
            if len(self.args.base_debs) > 1:
                apt_udeb.generate_packages_file('deb')
                apt_udeb.merge_pools(['deb', 'udeb'])
            else:
                apt_udeb.merge_pools(['udeb'])
            apt_udeb.generate_release_file()

            print("... completed generating metadata files")
            self.log.info("... completed generating metadata files")

        # Download the firmware debs if desired
        if len(self.args.firmware) > 0:
            self.log.info("Downloading firmware debs...")

            # FIXME: may need a change to the download location
            fw_root = self.cdroot['firmware'].path
            handler = get_apt_handler(fw_root,
                                      self.args.mirror,
                                      self.args.distribution,
                                      self.args.architecture)
            for pkg in self.args.firmware.split(' '):
                handler.download_package(pkg, fw_root)
            handler.clean_up_apt()
            self.log.info("... firmware deb downloads")

        # Generate boot config
        boot_timeout = self.args.boot_timeout
        if boot_timeout is not None:
            boot_timeout = int(boot_timeout)
        bootconfig = BootloaderConfig(self.cdroot.path, bootappend=self.args.bootappend, timeout=boot_timeout)

        if os.environ.get("LWR_DEBUG") is None or 'skipvm' not in os.environ['LWR_DEBUG']:
            bootconfig.add_live()
            locallivecfg = BootloaderConfig(self.cdroot.path, bootappend=self.args.bootappend, timeout=boot_timeout)
            locallivecfg.add_live_localisation()
            bootconfig.add_submenu('Debian Live with Localisation Support', locallivecfg)
        if self.args.installer:
            bootconfig.add_installer(self.kernel_path, self.ramdisk_path)

        # Install isolinux if selected
        if self.args.isolinux:
            self.log.info("Performing isolinux installation...")
            # FIXME: catch errors and cleanup.
            isolinux = Isolinux(os.path.join(self.args.work_dir, "isolinux"))
            isolinux.install(
                self.cdroot['isolinux'].path,
                self.args.mirror,
                self.args.distribution,
                self.args.architecture,
                bootconfig)

        # Install GRUB if selected
        if self.args.grub or self.args.grub_loopback_only:
            self.log.info("Performing GRUB installation...")
            install_grub(self.cdroot.path, bootconfig)  # FIXME: pass architecture & uefi settings.

        if self.args.customize_iso:
            self.run_cmd([self.args.customize_iso, self.cdroot.path])

        # Start the setup for building the ISO image
        xorriso = Xorriso(self.args.image_output,
                          self.args.volume_id,
                          isolinux=self.args.isolinux,
                          grub=self.args.grub)
        xorriso_args = xorriso.build_args(self.cdroot.path)
        if self.args.work_dir:
            xorriso.write_run_script(os.path.join(self.args.work_dir, "xorriso.sh"))

        # Install .disk information, including the args we just grabbed
        self.log.info("Installing the disk metadata ...")
        install_disk_info(self.cdroot, self.args.description, ' '.join(xorriso_args))

        # Create ISO image
        self.log.info("Creating the ISO image with Xorriso...")
        xorriso.build_image()

        # Remove the temporary directories
        self.log.info("Removing temporary work directories...")
        if self.args.installer:
            apt_udeb.clean_up_apt()
        print("Use the -cdrom option to test the image using qemu-system.")

    def run(self):
        parser = argparse.ArgumentParser(
                formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                description="Build a live Debian image")
        parser.add_argument('--version', action='version', version='%(prog)s ' + self.version)
        parser.add_argument("--log-level", action="store", default="debug", help="log at LEVEL, one of debug, info, warning, error, critical, fatal")
        parser.add_argument("--log", action="store", default="stderr", metavar="FILE", help="write log entries to FILE. Special values: stderr, none")
        self.add_settings(parser)

        self.args = parser.parse_args()

        log_format = "%(asctime)-15s %(levelname)s %(name)s %(message)s"
        levels = {
            'debug': logging.DEBUG,
            'info': logging.INFO,
            'warning': logging.WARNING,
            'error': logging.ERROR,
            'critical': logging.CRITICAL,
            'fatal': logging.FATAL,
        }
        if self.args.log == "stderr":
            logging.basicConfig(level=levels[self.args.log_level], stream=sys.stderr, format=log_format)
        elif self.args.log == "none":
            logging.basicConfig(level=levels[self.args.log_level], stream=open("/dev/null", "wt"), format="")
        else:
            logging.basicConfig(level=levels[self.args.log_level], filename=self.args.log, format="")

        try:
            if os.path.exists(self.args.image_output):
                raise Fail("Image '{}' already exists".format(self.args.image_output))
            if not self.args.isolinux and not self.args.grub:
                raise Fail("You must enable at least one bootloader!")
            if self.args.grub and self.args.grub_loopback_only:
                self.args.grub = False
            if os.geteuid() != 0:
                sys.exit("You need to have root privileges to run this script.")
            # FIXME: cleanup on error.

            self.start_ops()
        except Fail as e:
            print(e, file=sys.stderr)
            sys.exit(1)


def main():
    LiveWrapper(version=__version__).run()
