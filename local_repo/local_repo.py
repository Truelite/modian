#!/usr/bin/env python3

import argparse
import http.server
import os
import shutil


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
