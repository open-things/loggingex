"""Defines a helper context shortcut."""
from .change import ContextChange


class _ContextChangeShortcuts:
    def __call__(self, *args, **kwargs) -> ContextChange:
        """Create ContextChange object from positional and keyword arguments.

        :param args: passed into remove.
        :param kwargs: passed into update.
        :return: new ContextChange object.
        """
        return ContextChange().remove(*args).update(**kwargs)

    @staticmethod
    def fresh(**kwargs) -> ContextChange:
        """Create ContextChange object with fresh=True from keyword arguments.

        :param kwargs: passed into update.
        :return: new ContextChange object.
        """
        return ContextChange().fresh(True).update(**kwargs)


context = _ContextChangeShortcuts()
