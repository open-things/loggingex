"""Defines LoggingContextFilter and context helper.

LoggingContextFilter is class that you need to add to your loggers or handlers.

The context helper is function that you can use anywhere in your code to quickly
put value into the logging context.
"""
from logging import LogRecord

from .change import CONTEXT_STORE_CLASS, ContextChange
from .exceptions import (
    ContextChangeAlreadyStartedException,
    ContextChangeNotStartedException,
    ContextException,
    ContextInvalidNameException,
)
from .store import CONTEXT_STORE_VARIABLE_NAME, ContextStore

__all__ = (
    # exceptions
    "ContextChangeAlreadyStartedException",
    "ContextChangeNotStartedException",
    "ContextException",
    "ContextInvalidNameException",
    # internal-ish classes
    "ContextStore",
    "ContextChange",
    # settings
    "CONTEXT_STORE_VARIABLE_NAME",
    "CONTEXT_STORE_CLASS",
    # public api
    "LoggingContextFilter",
    "context",
)


class LoggingContextFilter:
    """Logging filter injects current context variables into the log records."""

    IGNORED_VARIABLE_NAMES = (
        "name",
        "msg",
        "args",
        "levelname",
        "levelno",
        "pathname",
        "filename",
        "module",
        "exc_info",
        "exc_text",
        "stack_info",
        "lineno",
        "funcName",
        "created",
        "msecs",
        "relativeCreated",
        "thread",
        "threadName",
        "processName",
        "process",
    )

    def filter(self, record: LogRecord):  # noqa: A003
        """Inject current context variables into the record.

        :param record: LogRecord to inject context into.
        :return: Always returns 1.
        """
        context_store = CONTEXT_STORE_CLASS()
        context = context_store.get()
        for name, value in context.items():
            if name not in self.IGNORED_VARIABLE_NAMES:
                setattr(record, name, value)
        return 1


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
