"""Defines LoggingContextFilter and context helper.

LoggingContextFilter is class that you need to add to your loggers or handlers.

The context helper is function that you can use anywhere in your code to quickly
put value into the logging context.
"""
from .change import ContextChange
from .exceptions import (
    ContextChangeAlreadyStartedException,
    ContextChangeNotStartedException,
    ContextException,
    ContextInvalidNameException,
)
from .filter import LoggingContextFilter
from .store import ContextStore


__all__ = (
    # exceptions
    "ContextChangeAlreadyStartedException",
    "ContextChangeNotStartedException",
    "ContextException",
    "ContextInvalidNameException",
    # internal-ish classes
    "ContextStore",
    "ContextChange",
    # public api
    "LoggingContextFilter",
    "context",
)


class _ContextChangeShortcuts:
    def __call__(self, *args, **kwargs) -> ContextChange:
        """Create ContextChange object from positional and keyword arguments.

        :param args: passed into remove.
        :param kwargs: passed into update.
        :return: new ContextChange object.
        """
        return ContextChange().remove(*args).update(**kwargs)

    @staticmethod
    def fresh(**kwargs) -> ContextChange:
        """Create ContextChange object with fresh=True from keyword arguments.

        :param kwargs: passed into update.
        :return: new ContextChange object.
        """
        return ContextChange().fresh(True).update(**kwargs)


context = _ContextChangeShortcuts()
