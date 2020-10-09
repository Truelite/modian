# live-wrapper - Wrapper for vmdebootstrap for creating live images
# (C) 2016 Neil Williams <codehelp@debian.org>
# See COPYING for terms of usage, modification and redistribution.
#
# lwr/apt.py - .apt folder helpers

# depends debian-archive-keyring vmdebootstrap python-apt

import os
import shutil
import tempfile
import logging
import apt
import apt_pkg
from lwr.utils import copytree, copy_files, Fail
from subprocess import check_output
import distro_info
from .component import Component

# handle a list of package names (udebs)
# handle a list of excluded package names
# handle a supplementary apt source for local udebs
# unique sort the combined package names


class AptUdebDownloader(Component):

    def __init__(self, destdir):
        super().__init__()
        self.architecture = 'armhf'
        self.mirror = None
        self.codename = None
        self.components = [
            'main/debian-installer', 'contrib/debian-installer',
            'non-free/debian-installer']
        self.dirlist = []
        self.cache = None
        self.destdir = destdir

    def prepare_apt(self):
        distroinfo = distro_info.DebianDistroInfo()
        if distroinfo.testing() == self.codename:
            self.suite = "testing"
        elif self.codename == "sid":
            self.suite = "unstable"
        else:
            self.suite = "stable"
        if not self.codename or not self.mirror:
            raise Fail("Misconfiguration: no codename or mirror set")
        state_dir = tempfile.mkdtemp()
        os.mkdir(os.path.join(state_dir, 'lists'))
        self.dirlist.append(state_dir)
        cache_dir = tempfile.mkdtemp()
        os.makedirs(os.path.join(cache_dir, 'archives', 'partial'))
        self.dirlist.append(cache_dir)
        etc_dir = tempfile.mkdtemp()
        os.mkdir(os.path.join(etc_dir, 'apt.conf.d'))
        os.mkdir(os.path.join(etc_dir, 'preferences.d'))
        os.mkdir(os.path.join(etc_dir, 'trusted.gpg.d'))
        copy_files(
            '/etc/apt/trusted.gpg.d',
            os.path.join(etc_dir, 'trusted.gpg.d')
        )
        with open(os.path.join(etc_dir, 'sources.list'), 'w') as sources:
            sources.write('deb %s %s %s\n' % (
                self.mirror, self.codename, ' '.join(self.components)))
        self.dirlist.append(etc_dir)
        updates = {
            'APT::Architecture': str(self.architecture),
            'APT::Architectures': str(self.architecture),
            'Dir::State': state_dir,
            'Dir::Cache': cache_dir,
            'Dir::Etc': etc_dir,
        }
        for key, value in updates.items():
            try:
                apt_pkg.config[key] = value  # pylint: disable=no-member
            except TypeError as exc:
                print(key, value, exc)
            continue

        self.cache = apt.cache.Cache()
        try:
            self.cache.update()
            self.cache.open()
        except apt.cache.FetchFailedException as exc:
            raise Fail('Unable to update cache: %s' % exc)
        if not os.path.exists(self.destdir):
            raise Fail('Destination directory %s does not exist' % self.destdir)

    def download_package(self, name, destdir):
        if not self.cache:
            raise Fail('No cache available.')
        if name not in self.cache:
            raise Fail('%s is not available' % name)
        pkg = self.cache[name]
        if not hasattr(pkg, 'versions'):
            raise Fail('%s has no available versions.' % name)
        # Pick the highest version of the package, in case there are >1
        versions = [v for v in pkg.versions if v.uri]
        if not versions:
            raise Fail('No downloadable version of {} found'.format(name))
        version = max(versions)
        if not version.uri:
            raise Fail('Not able to download %s' % name)
        filename = os.path.join(destdir, os.path.basename(version.record['Filename']))
        if os.path.exists(filename):
            self.log.info("Reusing existing %s", filename)
            return filename
        try:
            version.fetch_binary(destdir=destdir)
        except TypeError as exc:
            self.log.exception("fetch_binary failed")
            return None
        except apt.package.FetchError as exc:
            raise Fail('Unable to fetch %s: %s' % (name, exc))
        if os.path.exists(filename):
            return filename
        self.log.error("Downloading to %s did not produce file %s", destdir, os.path.basename(version.record['Filename']))
        return None

    def download_apt_file(self, pkg_name, pool_dir, fatal):
        if not self.cache:
            raise Fail('No cache available.')
        pkg = self.cache[pkg_name]
        if not hasattr(pkg, 'versions'):
            if fatal:
                raise Fail('%s has no available versions.' % pkg_name)
            return
        # Pick the highest version of the package, in case there are >1
        version = max(pkg.versions)
        if not version.uri:
            if fatal:
                raise Fail('Not able to download %s' % pkg_name)
            return
        prefix = version.source_name[0]
        # pool_dir is just a base, need to add main/[index]/[name]
        if version.source_name[:3] == 'lib':
            prefix = version.source_name[:4]
        pkg_dir = os.path.join(pool_dir, prefix, version.source_name)
        if not os.path.exists(pkg_dir):
            os.makedirs(pkg_dir)
        try:
            version.fetch_binary(destdir=pkg_dir)
        except TypeError as exc:
            return
        except apt.package.FetchError as exc:
            raise Fail('Unable to fetch %s: %s' % (pkg_name, exc))

    def download_udebs(self, exclude_list):
        # HACK HACK HACK
        # Setting up a separate pool for udebs, as apt-ftparchive
        # isn't generating separate Packages files
        pool_dir = os.path.join(self.destdir, '..', 'udeb', 'pool', 'main')
        if not os.path.exists(pool_dir):
            os.makedirs(pool_dir)
        for pkg_name in self.cache.keys():
            if pkg_name in exclude_list:
                continue
            self.download_apt_file(pkg_name, pool_dir, False)

    def download_base_debs(self, pkg_list):
        # HACK HACK HACK
        # Setting up a separate pool for debs, as apt-ftparchive
        # isn't generating separate Packages files
        pool_dir = os.path.join(self.destdir, '..', 'deb', 'pool', 'main')
        if not os.path.exists(pool_dir):
            os.makedirs(pool_dir)
        for pkg_name in pkg_list:
            self.download_apt_file(pkg_name, pool_dir, True)

    def generate_packages_file(self, style='udeb'):
        meta_dir = os.path.normpath(os.path.join(self.destdir, '..', 'dists',
                                                 self.codename,
                                                 'main',
                                                 'binary-%s' % (self.architecture,)))
        if style == 'udeb':
            meta_dir = os.path.normpath(os.path.join(self.destdir, '..', 'dists',
                                                     self.codename,
                                                     'main',
                                                     'debian-installer',
                                                     'binary-%s' % (self.architecture,)))

        current_dir = os.getcwd()
        os.chdir(os.path.join(self.destdir, '..', style))
        packages = check_output(['apt-ftparchive', '-o', 'Default::Packages::Extensions=.%s' % style,
                                 'packages', os.path.join('pool', 'main')])
        if not os.path.exists(meta_dir):
            os.makedirs(meta_dir)
        with open(os.path.join(meta_dir, 'Packages'), 'w') as pkgout:
            pkgout.write(packages)
        os.chdir(current_dir)

    # HACK HACK HACK
    # Move all the separate trees of debs, udebs and Packages files into the right place
    def merge_pools(self, sources):
        for source in sources:
            copytree(os.path.join(self.destdir, '..', source, 'pool'),
                     os.path.join(self.destdir, '..', 'pool'))
            shutil.rmtree(os.path.join(self.destdir, '..', source))

    def generate_release_file(self):
        release = check_output([
                'apt-ftparchive',
                '-o', 'APT::FTPArchive::Release::Origin=Debian',
                '-o', 'APT::FTPArchive::Release::Label=Debian',
                '-o', 'APT::FTPArchive::Release::Suite=%s' % (self.suite,),
                '-o', 'APT::FTPArchive::Release::Codename=%s' % (self.codename,),
                '-o', 'APT::FTPArchive::Release::Architectures=%s' % (self.architecture,),
                '-o', 'APT::FTPArchive::Release::Components=main',
                'release', os.path.abspath(os.path.join(self.destdir, '..', 'dists', self.codename))])
        with open(os.path.join(self.destdir, '..', 'dists', self.codename, 'Release'), 'w') as relout:
            relout.write(release)
        logging.info("Release file generated for CD-ROM pool.")
        # End mess ----------------------------------------------------

    def clean_up_apt(self):
        for clean in self.dirlist:
            if os.path.exists(clean):
                shutil.rmtree(clean)


def get_apt_handler(destdir, mirror, codename, architecture):
    apt_handler = AptUdebDownloader(destdir)
    apt_handler.mirror = mirror
    apt_handler.architecture = architecture
    apt_handler.codename = codename
    apt_handler.components = ['main', 'contrib', 'non-free']
    apt_handler.prepare_apt()
    return apt_handler
