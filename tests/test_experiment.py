class A:
    def __init__(self, calls=None):
        self.calls = calls or []

    def __enter__(self):
        self.calls.append("A: entering")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.calls.append("A: aborting")
        else:
            self.calls.append("A: leaving")
        return False


class B:
    def __init__(self, calls=None):
        self.calls = calls or []

    def __enter__(self):
        self.calls.append("B: entering")
        return A(calls=self.calls)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.calls.append("B: aborting")
        else:
            self.calls.append("B: leaving")
        return False


def test_a_no_error():
    with A() as a:
        assert isinstance(a, A)
        assert len(a.calls) == 1

    assert len(a.calls) == 2
    assert a.calls == ["A: entering", "A: leaving"]


def test_a_with_error():
    exc_caught = False
    try:
        with A() as a:
            assert isinstance(a, A)
            assert len(a.calls) == 1
            raise ValueError("boo")
    except ValueError:
        exc_caught = True
    assert exc_caught
    assert len(a.calls) == 2
    assert a.calls == ["A: entering", "A: aborting"]


def test_b_no_error():
    with B() as b:
        assert isinstance(b, A)
        assert len(b.calls) == 1

    assert len(b.calls) == 2
    assert b.calls == ["B: entering", "B: leaving"]


def test_b_with_error():
    exc_caught = False
    try:
        with B() as b:
            assert isinstance(b, A)
            assert len(b.calls) == 1
            raise ValueError("boo")
    except ValueError:
        exc_caught = True
    assert exc_caught
    assert len(b.calls) == 2
    assert b.calls == ["B: entering", "B: aborting"]
