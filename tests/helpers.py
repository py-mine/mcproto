from __future__ import annotations

import asyncio
import inspect
import unittest.mock
from collections.abc import Callable, Coroutine
from typing import Any, Generic, TypeVar

from typing_extensions import ParamSpec

T = TypeVar("T")
P = ParamSpec("P")
T_Mock = TypeVar("T_Mock", bound=unittest.mock.Mock)


def synchronize(f: Callable[P, Coroutine[Any, Any, T]]) -> Callable[P, T]:
    """This is a helper function, which takes an asynchronous function, and returns a synchronous alternative.

    This is needed because we sometimes want to test asynchronous behavior in a synchronous test function,
    where we can't simply await something. This function uses `asyncio.run` and generates a wrapper
    around the original asynchronous function, that awaits the result in a blocking synchronous way,
    returning the obtained value.
    """

    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        return asyncio.run(f(*args, **kwargs))

    return wrapper


class SynchronizedMixin:
    """Class acting as another wrapped object, with all async methods synchronized.

    This class needs :attr:`._WRAPPED_ATTRIBUTE` class variable to be set as the name of the internally
    held attribute, holding the object we'll be wrapping around.

    Child classes of this mixin will have their lookup logic changed, to instead perform a lookup
    on the wrapped attribute. Only if that lookup fails, we fallback to this class, meaning if both
    the wrapped attribute and this class have some attribute defined, the attribute from the wrapped
    object is returned. The only exceptions to this are lookup of the ``_WRAPPED_ATTRIBUTE`` variable,
    and of the attribute name stored under the ``_WRAPPED_ATTRIBUTE`` (the wrapped object).

    If the attribute held by the wrapped object is an asynchronous function, instead of returning it
    directly, the :func:`.synchronize` function will be called, returning a wrapped synchronous
    alternative for the requested async function.

    This is useful when we need to quickly create a synchronous alternative to a class holding async methods.
    However it isn't useful in production, since will cause typing issues (attributes will be accessible, but
    type checkers won't know that they exist here, because of the dynamic nature of this implementation).
    """

    _WRAPPED_ATTRIBUTE: str

    def __getattribute__(self, __name: str) -> Any:  # noqa: ANN401
        """Return attributes of the wrapped object, if the attribute is a coroutine function, synchronize it.

        The only exception to this behavior is getting the :attr:`._WRAPPED_ATTRIBUTE` variable itself, or the
        attribute named as the content of the ``_WRAPPED_ATTRIBUTE`` variable. All other attribute access will
        be delegated to the wrapped attribute. If the wrapped object doesn't have given attribute, the lookup
        will fallback to regular lookup for variables belonging to this class.
        """
        if __name == "_WRAPPED_ATTRIBUTE" or __name == self._WRAPPED_ATTRIBUTE:
            return super().__getattribute__(__name)

        wrapped = getattr(self, self._WRAPPED_ATTRIBUTE)

        if hasattr(wrapped, __name):
            obj = getattr(wrapped, __name)
            if inspect.iscoroutinefunction(obj):
                return synchronize(obj)
            return obj

        return super().__getattribute__(__name)

    def __setattr__(self, __name: str, __value: object) -> None:
        """Allow for changing attributes of the wrapped object.

        * If wrapped object isn't yet set, fall back to :meth:`~object.__setattr__` of this class.
        * If wrapped object doesn't already contain the attribute we want to set, also fallback to this class.
        * Otherwise, run ``__setattr__`` on it to update it.
        """
        try:
            wrapped = getattr(self, self._WRAPPED_ATTRIBUTE)
        except AttributeError:
            return super().__setattr__(__name, __value)
        else:
            if hasattr(wrapped, __name):
                return setattr(wrapped, __name, __value)

        return super().__setattr__(__name, __value)


class UnpropagatingMockMixin(Generic[T_Mock]):
    """This class is here to provide common functionality for our :class:`~unittest.mock.Mock` classes.

    By default, mock objects propagate themselves by returning a new instance of the same mock
    class, with same initialization attributes. THis is done whenever we're accessing new
    attributes that mock class.

    This propagation makes sense for simple mocks without any additional restrictions, however when
    dealing with limited mocks to some ``spec_set``, it doesn't usually make sense to propagate
    those same ``spec_set`` restrictions, since we generally don't have attributes/methods of a
    class be of/return the same class.

    This mixin class stops this propagation, and instead returns instances of specified mock class,
    defined in :attr:`.child_mock_type` class variable, which is by default set to
    :class:`~unittest.mock.MagicMock`, as it can safely represent most objects.

    .. note:
        This propagation handling will only be done for the mock classes that inherited from this
        mixin class. That means if the :attr:`.child_mock_type` is one of the regular mock classes,
        and the mock is propagated, a regular mock class is returned as that new attribute. This
        regular class then won't have the same overrides, and will therefore propagate itself, like
        any other mock class would.

        If you wish to counteract this, you can set the :attr:`.child_mock_type` to a mock class
        that also inherits from this mixin class, perhaps to your class itself, overriding any
        propagation recursively.
    """

    child_mock_type: T_Mock = unittest.mock.MagicMock

    # Since this is a mixin class, we can access some attributes defined in mock classes safely.
    # Define the types of these variables here, for proper static type analysis.
    _mock_sealed: bool
    _extract_mock_name: Callable[[], str]

    def _get_child_mock(self, **kwargs) -> T_Mock:
        """Method override which makes :attr:`.child_mock_type`` instances instead of instances of the same class.

        By default, this method creates a new mock instance of the same original class, and passes
        over the same initialization arguments. This overrides that behavior to instead create an
        instance of :attr:`.child_mock_type` class.
        """

        # Mocks can be sealed, in which case we wouldn't want to allow propagation of any kind
        # and rather raise an AttributeError, informing that given attr isn't accessible
        if self._mock_sealed:
            mock_name = self._extract_mock_name()
            if "name" in kwargs:
                obj_name = f"{mock_name}.{kwargs['name']}"
            else:
                obj_name = f"{mock_name}()"

            raise AttributeError(f"Can't access {obj_name}, mock is sealed.")

        # Propagate any other children as simple `unittest.mock.Mock` instances
        # rather than `self.__class__` instances
        return self.child_mock_type(**kwargs)


class CustomMockMixin(UnpropagatingMockMixin):
    """Provides common functionality for our custom mock types.

    * Stops propagation of same ``spec_set`` restricted mock in child mocks
      (see :class:`.UnpropagatingMockMixin` for more info)
    * Allows using the ``spec_set`` attribute as class attribute
    """

    spec_set = None

    def __init__(self, **kwargs):
        if "spec_set" in kwargs:
            self.spec_set = kwargs.pop("spec_set")
        super().__init__(spec_set=self.spec_set, **kwargs)  # type: ignore # Mixin class, this __init__ is valid
