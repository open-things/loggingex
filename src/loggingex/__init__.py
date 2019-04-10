"""A collection of extensions for the standard logging module."""

try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"

import loggingex.context as context

__all__ = ["__version__", "context"]
