#!/usr/bin/env python3

import argparse


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
        s_parser.set_defaults(func=self.serve)

        return parser

    def help(self, args):
        self.parser.print_help()

    def create(self, args):
        """
        Create a reprepro repository
        """

    def serve(self, args):
        """
        Serve a reprepro repository
        """

    def main(self):
        args = self.parser.parse_args()
        args.func(args)


if __name__ == '__main__':
    Repo().main()
