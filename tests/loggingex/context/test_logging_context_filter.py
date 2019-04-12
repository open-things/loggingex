from logging import DEBUG, LogRecord

from pytest import fixture, mark

from loggingex.context import LoggingContextFilter
from loggingex.context.filter import IGNORED_VARIABLE_NAMES
from .helpers import InitializedContextBase


class FilterTests(InitializedContextBase):
    @fixture()
    def record(self):
        return LogRecord(
            "test", DEBUG, "test.py", 1337, "message %d", (1,), None
        )

    def test_log_record_is_injected_with_context_variables(self, store, record):
        store.replace({"foo": 1, "bar": 2.3, "baz": "dummy"})
        assert LoggingContextFilter().filter(record) == 1
        assert record.foo == 1
        assert record.bar == 2.3
        assert record.baz == "dummy"

    @mark.parametrize("field", IGNORED_VARIABLE_NAMES)
    def test_ignores_variables_that_would_overwrite_record_fields(
        self, store, record, field
    ):
        store.replace({field: "overwrite", "foo": 1})
        LoggingContextFilter().filter(record)
        assert record.foo == 1
        assert getattr(record, field, "undefined") != "overwrite"
