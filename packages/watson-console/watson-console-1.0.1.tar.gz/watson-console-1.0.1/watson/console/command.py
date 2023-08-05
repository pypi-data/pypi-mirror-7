# -*- coding: utf-8 -*-
import abc
from watson.common.contextmanagers import suppress


class Base(metaclass=abc.ABCMeta):
    """The base command that outlines the required structure for a console
    command.

    Help is automatically invoked when the `-h` or `--help` option is used.

    http://docs.python.org/dev/library/argparse.html#the-add-argument-method

    Example:

    .. code-block:: python

        # can be executed by `script.py mycommand`
        class MyCommand(BaseCommand):
            name = 'mycommand'

            def execute(self):
                return True

        # can be executed by `script.py mycommand -t something`
        class MyCommand(BaseCommand):
            name = 'mycommand'
            arguments = [
                (['-t', '--test'], {'help': 'Do something with -t'})
            ]

            def execute(self):
                return True if self.parsed_args.t else False

        # can be executed by `script.py mycommand something`
        class MyCommand(BaseCommand):
            name = 'mycommand'
            arguments = [
                {'dest': 'argument1', 'help': 'This is the help for the argument'}
            ]

            def execute(self):
                return True if self.parsed_args.argument1 else False
    """
    name = None
    arguments = []
    help = 'Missing help.'
    _parsed_args = None

    @property
    def parsed_args(self):
        """Returns the parsed arguments.

        Returns:
            list|dict depending on whether or not there have been named arguments.
        """
        return self._parsed_args

    @parsed_args.setter
    def parsed_args(self, args):
        """Set the parsed arguments.
        """
        self._parsed_args = args

    @abc.abstractmethod
    def execute(self):
        raise NotImplementedError('execute() must be implemented.')  # pragma: no cover

    def __call__(self):
        return self.execute()


def find_commands_in_module(module):
    """Retrieves a list of all commands within a module.

    Returns:
        A list of commands from the module.
    """
    commands = []
    for key in dir(module):
        item = getattr(module, key)
        with suppress(Exception):
            if issubclass(item, Base) and item != Base:
                commands.append(item)
    return commands
