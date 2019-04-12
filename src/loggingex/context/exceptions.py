"""Exceptions used by loggingex.context."""
from ..exceptions import LoggingExtensionsException


class ContextException(LoggingExtensionsException):
    pass


class ContextInvalidNameException(ContextException):
    pass


class ContextChangeAlreadyStartedException(ContextException):
    pass


class ContextChangeNotStartedException(ContextException):
    pass
