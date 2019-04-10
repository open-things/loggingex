from loggingex.context import ContextChange, context


def test_context_creates_context_change():
    change = context("foo", bar="baz")
    assert isinstance(change, ContextChange)
    assert change.context_fresh is False
    assert change.context_remove == {"foo"}
    assert change.context_update == {"bar": "baz"}
    assert change.context_restore_token is None


def test_context_fresh_creates_context_change():
    change = context.fresh(bar="baz")
    assert isinstance(change, ContextChange)
    assert change.context_fresh is True
    assert change.context_remove == set()
    assert change.context_update == {"bar": "baz"}
    assert change.context_restore_token is None
