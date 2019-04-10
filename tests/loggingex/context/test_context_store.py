from loggingex.context import ContextStore
from .helpers import InitializedContextBase, ResetContextBase


class InitializeContextTests(ResetContextBase):
    def test_creates_and_initializes_context_variable(self):
        assert ContextStore._context is None
        ContextStore.initialize_context()
        assert ContextStore._context is not None

    def test_does_nothing_after_first_initialization(self):
        ContextStore.initialize_context()
        ctxvar = ContextStore._context
        ContextStore.initialize_context()
        assert ContextStore._context is ctxvar


class ContextPropertyTests(InitializedContextBase):
    def test_returns_singleton_instance_of_contextvar(self):
        assert ContextStore().context is ContextStore._context

    def test_returns_same_contextvar_instance(self):
        store1, store2 = ContextStore(), ContextStore()
        assert store1.context is store2.context


class GetTests(InitializedContextBase):
    def test_returns_an_empty_dict_initially(self, store):
        assert store.get() == {}

    def test_returns_a_currently_stored_dictionary(self, store):
        store.context.set({"t": "test_returns_a_currently_stored_dictionary"})
        assert ContextStore().get() == {
            "t": "test_returns_a_currently_stored_dictionary"
        }


class ReplaceTests(InitializedContextBase):
    def test_saves_given_dict(self, store):
        store.replace({"t": "test_saves_given_dict"})
        assert store.context.get() == {"t": "test_saves_given_dict"}

    def test_returns_a_token_to_be_used_to_restore_context_state(self, store):
        token = store.replace(
            {"t": "test_returns_a_token_to_be_used_to_restore_context_state"}
        )
        store.context.reset(token)
        assert store.context.get() == {}


class RestoreTests(InitializedContextBase):
    def test_restores_context_to_state_represented_by_given_token(self, store):
        token = store.context.set(
            {"t": "test_restores_context_to_state_represented_by_given_token"}
        )
        store.restore(token)
        assert store.context.get() == {}
