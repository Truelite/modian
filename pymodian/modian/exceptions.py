from __future__ import annotations


class ModianError(RuntimeError):
    """
    Exception that gets caught to make the program exit with an error.

    Use this as a kind of RuntimeError where the user input or system
    configuration is likely to blame.
    """


class ActionNotImplementedError(NotImplementedError):
    """
    Exception raised when an action is still not implemented.
    """
