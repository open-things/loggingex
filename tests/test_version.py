import loggingex


def test_version_is_defined():
    assert hasattr(loggingex, "__version__")
    assert loggingex.__version__ != "unknown"
