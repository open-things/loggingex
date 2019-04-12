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
from .shortcuts import context
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
