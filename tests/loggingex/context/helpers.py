from pytest import fixture

from loggingex.context import ContextStore


class ResetContextBase:
    @fixture()
    def store(self):
        return ContextStore()

    @fixture(autouse=True)
    def reset_context_variable(self):
        ContextStore._context = None


class InitializedContextBase(ResetContextBase):
    @fixture(autouse=True)
    def initialized_context(self, reset_context_variable):
        ContextStore.initialize_context()
