"""A collection of extensions for the standard logging module."""

try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"

from .exceptions import LoggingExtensionsException

__all__ = ["__version__", "LoggingExtensionsException"]
