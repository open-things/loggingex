"""Defines ContextChange class."""
from contextvars import Token
from functools import partial, wraps
from itertools import chain
from operator import contains
from typing import Any, AnyStr, Iterable, Optional, Set

from .exceptions import (
    ContextChangeAlreadyStartedException,
    ContextChangeNotStartedException,
    ContextInvalidNameException,
)
from .store import ContextStore, ContextType

ContextUpdateType = ContextType
ContextRemoveType = Set[AnyStr]
ContextVariableUnvalidatedName = Any
ContextVariableUnvalidatedNames = Iterable[ContextVariableUnvalidatedName]


class ContextChange:
    """Represents an atomic context change.

    Context change consists of a list of context variables to be removed and a
    name=value mapping of new variables or overrides for the existing variables.

    Actual context change does not happen until start method is called.

    Context is restored, when stop method is called.
    """

    context_fresh = False  # type: bool
    context_remove = None  # type: ContextRemoveType
    context_update = None  # type: ContextUpdateType
    context_restore_token = None  # type: Optional[Token]

    def __init__(
        self,
        context_fresh: bool = False,
        context_remove: ContextRemoveType = None,
        context_update: ContextUpdateType = None,
        context_restore_token: Token = None,
    ):
        self.context_fresh = context_fresh
        self.context_remove = set()
        self.context_update = {}

        self.context_restore_token = None  # needed for validation
        if context_remove:
            self.remove(*context_remove)
        if context_update:
            self.update(**context_update)

        self.context_restore_token = context_restore_token

    def __str__(self) -> str:
        parts = [
            "!" if self.context_restore_token else None,
            "-*" if self.context_fresh else None,
        ]
        parts.extend("-%s" % n for n in sorted(self.context_remove))
        upd = self.context_update
        val = self.context_update.__getitem__
        parts.extend("+%s=%r" % (n, val(n)) for n in sorted(upd.keys()))

        return " ".join(x for x in parts if x)

    def __repr__(self):
        return "<ContextChange: %s>" % str(self)

    @classmethod
    def validate_context_variable_name(
        cls, name: ContextVariableUnvalidatedName
    ) -> None:
        """Validate given object as a context variable name.

        Names must be valid python identifiers.

        ContextInvalidNameException is raised if the object is not a valid name.
        """
        if not isinstance(name, str):
            raise ContextInvalidNameException(
                "Context variable name must be a string", name
            )
        if not name.isidentifier():
            raise ContextInvalidNameException(
                "Context variable name must be a valid python identifier", name
            )

    @classmethod
    def validate_context_variable_names(
        cls, names: ContextVariableUnvalidatedNames
    ) -> None:
        """Validate given objects as context variable names.

        Names must be valid python identifiers.

        ContextInvalidNameException is raised if at least one object is not a
        valid name.
        """
        for name in names:
            cls.validate_context_variable_name(name)

    @property
    def started(self) -> bool:
        """Return True if this context change instance already started.

        :return: True if context change is started, False otherwise.
        """
        return self.context_restore_token is not None

    def can_change(self, raise_on_fail: bool = False) -> bool:
        """Return True if this context change has not been started yet.

        :param raise_on_fail: instead of returning False - raise an exception.
        :return: True if context change has not been started, False otherwise.
        """
        if raise_on_fail and self.started:
            raise ContextChangeAlreadyStartedException(
                "Context change can not be updated"
            )
        return not self.started

    def fresh(self, value: bool = True) -> "ContextChange":
        """Tell to create clean or reuse old context.

        If fresh is set to True, the context_remove does not really matter,
        because empty dictionary will be used as starting point for this change.
        If fresh is set to False, then old context will be changed according to
        context_remove and context_update.

        :param value: fresh value.
        :return: self (so that calls can be chained).
        """
        self.can_change(raise_on_fail=True)
        self.context_fresh = value
        return self

    def remove(self, *context_remove) -> "ContextChange":
        """Add variable removes to the ContextChange.

        :param context_remove: names to be removed from context on start.
        :return: self (so that calls can be chained).
        """
        self.can_change(raise_on_fail=True)
        self.validate_context_variable_names(context_remove)
        self.context_remove.update(context_remove)
        return self

    def update(self, **context_update) -> "ContextChange":
        """Add variable updates to the ContextChange.

        :param context_update: variables to be set in context on start.
        :return: self (so that calls can be chained).
        """
        self.can_change(raise_on_fail=True)
        self.validate_context_variable_names(context_update.keys())
        self.context_update.update(context_update)
        return self

    def apply(self, context: ContextType) -> ContextType:
        """Return given context with changes applied.

        Given context will be ignored (as well as context removes) if
        self.context_fresh is True. Otherwise, variables will removed from given
        context first, then updated will be applied.

        Note: context dictionary will not be modified - new dictionary will be
        constructed instead.

        :param context: initial context dictionary.
        :return: changed context dictionary.
        """
        context = context.items()
        if self.context_fresh:
            context = []
        elif self.context_remove:
            checker = partial(contains, self.context_remove)
            context = ((k, v) for k, v in context if not checker(k))
        if self.context_update:
            context = chain(context, self.context_update.items())
        return dict(context)

    def start(self) -> None:
        """Apply context change to the global logging context store."""
        if self.started:
            raise ContextChangeAlreadyStartedException(
                "Context change already started"
            )
        context_store = ContextStore()
        context = self.apply(context_store.get())
        self.context_restore_token = context_store.replace(context)

    def stop(self) -> None:
        """Restore global logging context store to previous state."""
        if not self.started:
            raise ContextChangeNotStartedException(
                "Context change has not been started"
            )
        context_store = ContextStore()
        context_store.restore(self.context_restore_token)
        self.context_restore_token = None

    def __enter__(self) -> "ContextChange":
        """Allow ContextChange to be used as context manager.

        This simply calls start method and returns self.

        :return: self.
        """
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        """Allow ContextChange to be used as context manager.

        This simply calls stop method and returns False.

        :param exc_type: Exception type.
        :param exc_val: Exception value.
        :param exc_tb: Exception traceback.
        :return: False
        """
        self.stop()
        return False

    def __call__(self, func):  # noqa: D202
        """Allow ContextChange to be used as function decorator.

        :param func: A callable to decorated.
        :return: Decorated callable.
        """

        @wraps(func)
        def decorated(*args, **kwargs):
            # copy self and the apply it
            # https://github.com/open-things/loggingex/issues/8
            context_change = ContextChange(
                context_fresh=self.context_fresh,
                context_remove=self.context_remove,
                context_update=self.context_update,
            )
            with context_change:
                return func(*args, **kwargs)

        return decorated
