from pytest import fixture, mark

from loggingex.wsgi.util import (
    get_request_headers,
    get_request_info,
    get_wsgi_info,
    unicode,
)


@fixture()
def wsgi_environ():
    environ = {}
    environ.update(
        {
            "wsgi.version": (1, 0),
            "wsgi.url_scheme": "https",
            "wsgi.multiprocess": 0,
            "wsgi.multithread": 1,
            "wsgi.run_once": 0,
        }
    )
    environ.update(
        {
            "REQUEST_METHOD": "POST",
            "SCRIPT_NAME": "/foo",
            "PATH_INFO": "/bar/baz",
            "QUERY_STRING": "dummy=1",
            "SERVER_NAME": "backend",
            "SERVER_PORT": "8000",
            "SERVER_PROTOCOL": "HTTP/1.1",
            "CONTENT_TYPE": "application/json",
            "CONTENT_LENGTH": "1337",
            "HTTPS": "1",
        }
    )
    environ.update(
        {
            "HTTP_USER_AGENT": "UnitTest",
            "HTTP_HOST": "example.io",
            "HTTP_X_FORWARDED_FOR": "111.222.112.221",
            "HTTP_X_FORWARDED_PROTO": "https",
            "HTTP_X_REQUEST_ID": "1a2a3a4a5a6a7a8a",
        }
    )
    return environ


@mark.parametrize("arg,ret", [("a", "a"), (b"b", "b"), (1, "1")])
def test_unicode_converts_anything_to_string(arg, ret):
    assert unicode(arg) == ret


def test_get_wsgi_info_returns_wsgi_information(wsgi_environ):
    info = get_wsgi_info(wsgi_environ)
    assert info["wsgi_version_tuple"] == (1, 0)
    assert info["wsgi_version"] == "1.0"
    assert info["wsgi_url_scheme"] == "https"
    assert info["wsgi_multiprocess"] == 0
    assert info["wsgi_multithread"] == 1
    assert info["wsgi_run_once"] == 0


def test_get_request_info(wsgi_environ):
    info = get_request_info(wsgi_environ)
    assert info["request_method"] == "POST"
    assert info["request_script_name"] == "/foo"
    assert info["request_path_info"] == "/bar/baz"
    assert info["request_query_string"] == "dummy=1"
    assert info["request_server_name"] == "backend"
    assert info["request_server_port"] == "8000"
    assert info["request_server_protocol"] == "HTTP/1.1"
    assert info["request_content_type"] == "application/json"
    assert info["request_content_length"] == "1337"
    assert info["request_uri"] == "https://example.io/foo/bar/baz?dummy=1"
    assert info["request_application_uri"] == "https://example.io/foo"


def test_get_request_headers(wsgi_environ):
    info = get_request_headers(wsgi_environ)
    assert info["header_user_agent"] == "UnitTest"
    assert info["header_host"] == "example.io"
    assert info["header_x_forwarded_for"] == "111.222.112.221"
    assert info["header_x_forwarded_proto"] == "https"
    assert info["header_x_request_id"] == "1a2a3a4a5a6a7a8a"
