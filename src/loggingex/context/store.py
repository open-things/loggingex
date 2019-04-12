"""Defines ContextStore class."""
from contextvars import ContextVar, Token
from typing import Any, AnyStr, ClassVar, Dict

ContextType = Dict[AnyStr, Any]

CONTEXT_STORE_VARIABLE_NAME = "LOGGINGEX__CONTEXT__STORE"


class ContextStore:
    """ContextStore class is used to save/load/restore contexts.

    It is a thin wrapper around contextvars.ContextVar object.
    """

    _context = None  # type: ClassVar[ContextVar[ContextType]]

    @classmethod
    def initialize_context(cls):
        """Ensure private static context is initialized."""
        if not ContextStore._context:
            ContextStore._context = ContextVar(CONTEXT_STORE_VARIABLE_NAME)
            ContextStore._context.set({})

    @property
    def context(self) -> ContextVar[ContextType]:
        """Public singleton for the static context."""
        return ContextStore._context

    def get(self) -> ContextType:
        """Return current context."""
        self.initialize_context()
        ctx = self.context.get({})
        return ctx

    def replace(self, ctx: ContextType) -> Token:
        """Replace current context with a new one.

        :param ctx: new context.
        :return: token, to be passed to restore.
        """
        self.initialize_context()
        token = self.context.set(ctx)
        return token

    def restore(self, token: Token) -> None:
        """Restore context.

        :param token: token to be restored to.
        """
        self.initialize_context()
        self.context.reset(token)
