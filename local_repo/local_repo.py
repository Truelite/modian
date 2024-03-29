#!/usr/bin/env python3

import argparse
import http.server
import os
import shutil
import subprocess


def _get_first_docstring_line(obj):
    try:
        return obj.__doc__.split('\n')[1].strip()
    except (AttributeError, IndexError):
        return None


class Repo:
    """
    Manage a local reprepro repository
    """
    def __init__(self):
        self.parser = self._get_parser()

    def _get_parser(self):
        parser = argparse.ArgumentParser(
            description=_get_first_docstring_line(self)
        )
        parser.set_defaults(func=self.help)

        # ****** Common options
        parser.add_argument(
            '--directory', '-d',
            default='repo',
            help='Path to a directory for the local repository'
                 + '(default: repo)',
        )

        # ****** Subcommands
        subparsers = parser.add_subparsers()

        # Create
        c_parser = subparsers.add_parser(
            'create',
            help=_get_first_docstring_line(self.create),
        )
        c_parser.set_defaults(func=self.create)

        # Add
        a_parser = subparsers.add_parser(
            'add-deb',
            help=_get_first_docstring_line(self.add_deb),
        )
        a_parser.add_argument(
            '--distro', '-d',
            default='trixie',
            help='target distribution (default: trixie)',
        )
        a_parser.add_argument(
            '--force', '-f',
            action="store_true",
            help='delete existing package before installing',
        )
        a_parser.add_argument(
            'deb',
            nargs='+',
            help='.deb package(s) to add',
        )
        a_parser.set_defaults(func=self.add_deb)

        # Remove
        r_parser = subparsers.add_parser(
            'remove',
            help=_get_first_docstring_line(self.remove),
        )
        r_parser.add_argument(
            'package',
            help='package to remove',
        )
        r_parser.set_defaults(func=self.remove)

        # Serve
        s_parser = subparsers.add_parser(
            'serve',
            help=_get_first_docstring_line(self.serve),
        )
        s_parser.add_argument(
            '--port', '-p',
            default=8099,
            help='port for the local repository (default: 8099)',
        )
        s_parser.set_defaults(func=self.serve)

        return parser

    def main(self):
        args = self.parser.parse_args()
        args.func(args)

    def help(self, args):
        self.parser.print_help()

    def create(self, args):
        """
        Create a reprepro repository
        """
        confdir = os.path.join(args.directory, 'conf')
        scriptdir = os.path.dirname(os.path.abspath(__file__))
        os.makedirs(confdir, exist_ok=True)
        shutil.copyfile(
            os.path.join(scriptdir, 'conf/distributions'),
            os.path.join(confdir, 'distributions'),
        )
        shutil.copyfile(
            os.path.join(scriptdir, 'conf/options'),
            os.path.join(confdir, 'options'),
        )

    def remove(self, args):
        """
        Remove a package from all distributions
        """
        os.chdir(args.directory)
        codenames = []
        res = subprocess.run(
            [
                'reprepro',
                '-b', '.',
                'ls',
                args.package,
            ],
            capture_output=True,
        )
        for lin in res.stdout.decode().split("\n"):
            try:
                cn = lin.split("|")[2].strip()
                codenames.append(cn)
            except IndexError:
                pass
        for cn in codenames:
            subprocess.run(
                [
                    'reprepro',
                    '-b', '.',
                    'remove',
                    cn,
                    args.package,
                ]
            )

    def add_deb(self, args):
        """
        Add a .deb to the reprepro repository
        """
        deb_files = []
        for fname in args.deb:
            deb_files.append(os.path.abspath(fname))
        pkg_names = [os.path.basename(n).split("_")[0] for n in deb_files]
        os.chdir(args.directory)
        if args.force:
            subprocess.run(
                [
                    'reprepro',
                    '-b', '.',
                    'remove',
                    args.distro,
                    *pkg_names,
                ]
            )
        subprocess.run(
            [
                'reprepro',
                '-b', '.',
                'includedeb',
                args.distro,
                *deb_files,
            ]
        )

    def serve(self, args):
        """
        Serve a reprepro repository
        """
        os.chdir(args.directory)
        httpd = http.server.HTTPServer(
            ('', args.port),
            http.server.SimpleHTTPRequestHandler,
        )
        httpd.serve_forever()


if __name__ == '__main__':
    Repo().main()
