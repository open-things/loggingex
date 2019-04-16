from logging import Logger, getLogger

from pytest import fixture
from webtest import TestApp as WSGITestApp

from loggingex.context import LoggingContextFilter
from loggingex.wsgi import RequestContextMiddleware


class DummyApp:
    DEFAULT_CONTENT = (
        "404 Not Found",
        {"Content-Type": "text/plain"},
        ["Not Found:", "{path_info}", "\n"],
    )

    def __init__(self, content, logger=None):
        self.content = content or {}
        if isinstance(logger, Logger):
            self.logger = logger
        elif isinstance(logger, str):
            self.logger = getLogger(logger)
        else:
            self.logger = getLogger()

    def __call__(self, environ, start_response):
        path_info = environ["PATH_INFO"]
        self.logger.debug("Handling request: %s", path_info)
        status, headers, content = self.content.get(
            path_info, self.DEFAULT_CONTENT
        )
        headers = list(headers.items())
        self.logger.debug("Sending response %r with: %r", status, headers)
        start_response(status, headers)
        for block in content:
            block = block.format(path_info=path_info, environ=environ)
            block = block.encode("utf-8")
            yield block
        self.logger.info("%s: %s", path_info, status)


@fixture()
def logger(caplog):
    caplog.set_level("DEBUG", "app")
    logger = getLogger("app")
    logger.addFilter(LoggingContextFilter())


@fixture()
def dummyapp(logger):
    content = {
        "/": ("200 Ok", {"Content-Type": "text/plain"}, ["Hello, ", "World!"])
    }
    app = DummyApp(content, logger)
    app = RequestContextMiddleware(app, headers=True, wsgi_info=True)
    return WSGITestApp(app)


def test_request_context_is_added_to_logging_records(caplog, logger, dummyapp):
    response = dummyapp.get("/")
    assert response.status_code == 200
    assert "Hello, World!" in response

    for record in caplog.records:
        assert record.name == logger.name
        assert record.request_method == "GET"
        assert record.request_path_info == "/"
