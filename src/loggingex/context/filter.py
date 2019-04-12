"""Defines LoggingContextFilter class."""
from logging import LogRecord

from .store import ContextStore

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


class LoggingContextFilter:
    """Logging filter injects current context variables into the log records."""

    def filter(self, record: LogRecord):  # noqa: A003
        """Inject current context variables into the record.

        :param record: LogRecord to inject context into.
        :return: Always returns 1.
        """
        context_store = ContextStore()
        context = context_store.get()
        for name, value in context.items():
            if name not in IGNORED_VARIABLE_NAMES:
                setattr(record, name, value)
        return 1
