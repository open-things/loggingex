"""Defines a WSGI request context middleware."""
from .util import get_wsgi_request_context
from ..context import context


class RequestContextMiddleware:
    """WSGI middleware, that adds WSGI environ information to logging context.

    This is meant to ve used together with the `LoggingContextFilter`.

    The only thing this middleware does, is it wraps the
    `app(environ, start_response)` call within the `loggingex.context.context`
    context manager, where it sets configured WSGI information extracted from
    `environ` argument in the context.

    :param app: WSGI application to be wrapped by this middleware.
    :param headers: Include request headers in the context.
    :param wsgi_info: Include WSGI information in the context.
    """

    def __init__(self, app, headers: bool = True, wsgi_info: bool = False):
        self.app = app
        self.headers = headers
        self.wsgi_info = wsgi_info

    def __call__(self, environ, start_request):
        request_context = get_wsgi_request_context(
            environ, wsgi_info=self.wsgi_info, headers=self.headers
        )
        with context(**request_context):
            for item in self.app(environ, start_request):
                yield item
