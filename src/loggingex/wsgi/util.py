"""Defines information extraction from WSGI environ functions."""
from typing import Any, AnyStr, Mapping
from wsgiref import util

from ..context.change import ContextType

EnvironType = Mapping[AnyStr, Any]


def unicode(value: Any) -> str:
    """Convert a value to a string.

    This function, is essentially a wrapper for the built-in `str` function,
    with one difference - if the argument is wither `bytes` or `bytearray`, then
    it will be properly "decoded" (using "latin-1" encoding).

    :param value: Value to be converted to a string.
    :return: String representation of the value.
    """
    if isinstance(value, (bytes, bytearray)):
        value = value.decode("latin-1")
    if not isinstance(value, str):
        value = str(value)
    return value


def get_wsgi_info(environ: EnvironType) -> ContextType:
    """Extract logging context friendly wsgi information.

    Extract all non-stream values from environ, that start with "wsgi." and add
    them to the result dictionary with "wsgi_" prefix.

    Note, that the original "wsgi.version" value is added as
    "wsgi_version_tuple", while "wsgi_version" in the result dictionary is a
    string representation of the version. For example, if "wsgi.version" was
    `(1, 0)`, then the resulting string would be `"1.0"`.

    :param environ: WSGI environ (as it is passed to WSGI application).
    :return: A logging context friendly mapping of WSGI information.
    """
    wsgi_info = {
        "wsgi_version_tuple": environ["wsgi.version"],
        "wsgi_version": ".".join(str(v) for v in environ["wsgi.version"]),
        "wsgi_url_scheme": unicode(environ["wsgi.url_scheme"]),
        "wsgi_multiprocess": environ["wsgi.multiprocess"],
        "wsgi_multithread": environ["wsgi.multithread"],
        "wsgi_run_once": environ["wsgi.run_once"],
    }
    return wsgi_info


def get_request_info(environ: EnvironType) -> ContextType:
    """Extract logging context friendly request and server information.

    Extract all values related to server and to the specific request, such as
    `SERVER_NAME`, `SERVER_PORT`, `PATH_INFO`, `QUERY_STRING`.

    The names in the resulting dictionary are the same, but converted to
    lowercase and prefixed with "request_".

    In addition to these values, two calculated values are also added -
    `request_uri` and `request_application_uri`. These values are calculated
    using `wsgiref.util` functions `request_uri` (with `include_query=True`) and
    `application_uri`.

    :param environ: WSGI environ (as it is passed to WSGI application).
    :return: A logging context friendly mapping of request and server
        information.
    """
    request_info = {
        "request_method": unicode(environ["REQUEST_METHOD"]),
        "request_script_name": unicode(environ["SCRIPT_NAME"]),
        "request_path_info": unicode(environ["PATH_INFO"]),
        "request_query_string": unicode(environ.get("QUERY_STRING", "")),
        "request_server_name": unicode(environ["SERVER_NAME"]),
        "request_server_port": unicode(environ["SERVER_PORT"]),
        "request_server_protocol": unicode(environ["SERVER_PROTOCOL"]),
        "request_content_type": unicode(environ.get("CONTENT_TYPE", "")),
        "request_content_length": unicode(environ.get("CONTENT_LENGTH", "")),
        "request_uri": unicode(util.request_uri(environ, include_query=True)),
        "request_application_uri": unicode(util.application_uri(environ)),
    }
    return request_info


def get_request_headers(environ: EnvironType) -> ContextType:
    """Extract logging context friendly request headers.

    All headers are added to the result as is, their WSGI names are converted to
    lowercase and "HTTP_" prefix is replaced with "header_" prefix.

    :param environ: WSGI environ (as it is passed to WSGI application).
    :return: A logging context friendly mapping of request headers.
    """
    request_headers = {}

    headers = ((k, v) for k, v in environ.items() if k.startswith("HTTP_"))
    for key, value in headers:
        header = key[5:]  # drop "HTTP_" prefix
        header = header.lower()
        request_headers["header_" + header] = value

    return request_headers


def get_wsgi_request_context(
    environ: EnvironType, headers: bool = True, wsgi_info: bool = False
) -> ContextType:
    """Extract logging context friendly information from WSGI environ mapping.

    This function wraps `get_request_info`, `get_request_headers` and
    `get_wsgi_info` functions.

    The result will always include values returned by `get_request_info`
    function.

    If `headers` is `True`, result will include values returned by
    `get_request_headers` function.

    If `wsgi_info` is `True`, result will include values returned by
    `get_wsgi_info` function.

    :param environ: WSGI environ (as it is passed to WSGI application).
    :param headers: Include request header information in the result.
    :param wsgi_info: Include WSGI information in the result.
    :return: A logging context friendly mapping of values.
    """
    request_context = {}
    request_context.update(get_request_info(environ))
    if headers:
        request_context.update(get_request_headers(environ))
    if wsgi_info:
        request_context.update(get_wsgi_info(environ))
    return request_context
