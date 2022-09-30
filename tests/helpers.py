from __future__ import annotations

import asyncio
import inspect
import unittest.mock
from collections.abc import Callable, Coroutine
from typing import Any, TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from typing_extensions import ParamSpec

    P = ParamSpec("P")

T = TypeVar("T")


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
    """Class responsible for automatically synchronizing asynchronous functions in wrapped attribute.

    This class needs `_WRAPPED_ATTRIBUTE` class variable to be set as the name of the internally held
    attribute, with some asynchronous functions in it, which we should be wrapping around.

    Classes inheriting from this mixin class will first look up attributes stored in the wrapped version,
    and only if the wrapped object doesn't contain this attribute, the lookup will fall back to internal
    attributes. (i.e. if the object held under wrapped attribute name had `foo` method, and so does the
    child class of this mixin, accessing `foo` will return `foo` method held by the wrapped object, not
    the one held by this class.) The only exceptions to this is looking up the `_WRAPPED_ATTRIBUTE` class
    variable, and looking up the attribute stored under this variable.

    If the attribute held by the wrapped object is an asynchronous function, it will be wrapped with the
    `synchronize` decorator, otherwise it will be returned without any modifications.

    This is useful when we need to quickly create a synchronous alternative to a class holding async methods.
    However it isn't useful in production, since will cause typing issues (attributes will be accessible, but
    type checkers won't know that they exist here, because of the dynamic nature of this implementation).
    """

    _WRAPPED_ATTRIBUTE: str

    def __getattribute__(self, __name: str) -> Any:  # noqa: ANN401
        """Return attributes of the wrapped object, if the attribute is a coroutine, synchronize it.

        The only exception to this behavior is getting the wrapped attribute parameter, or attribute named as the
        content of the wrapped parameter. All other attribute access will be delegated to the wrapped attribute.
        If the wrapped object doesn't have given attribute, this will however still fallback to lookup on this class.
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

        - If wrapped object isn't yet set, fall back to setattr of this class.
        - If wrapped object doesn't already have attribute we want to set, also fallback to this class.
        - Otherwise, if the wrapped object does have the attribute we want to set, run setattr on it to update it.
        """
        try:
            wrapped = getattr(self, self._WRAPPED_ATTRIBUTE)
        except AttributeError:
            return super().__setattr__(__name, __value)
        else:
            if hasattr(wrapped, __name):
                return setattr(wrapped, __name, __value)

        return super().__setattr__(__name, __value)


class UnpropagatingMockMixin:
    """
    This class is here to provide common functionality for our mock classes.

    By default, mock objects propagate themselves by returning a new instance of the same
    custom mock class when accessing new attributes of given mock class. This makes sense
    for simple mocks without any additional restrictions, however when dealing with limited
    mocks to some `spec_set`, it doesn't make sense to propagate those same set restrictions,
    since we generally don't have methods of some class be of the same class.
    """

    spec_set = None

    # Since this is a mixin class, we can access some attributes defined in mock classes safely
    # define the types of these variables here, for proper static type analysis
    _mock_sealed: bool
    _extract_mock_name: Callable[[], str]

    def _get_child_mock(self, **kwargs) -> unittest.mock.Mock:
        """
        Method override which generates pure `unittest.mock.Mock` instances instead of instances of the same class.

        By default, this method creates a new mock instance of the same original class (self.__class__) for newly
        accessed attributes. However this doesn't make sense for mocks limited to some spec_set, since we don't
        expect the available attributes to hold instances of the same class, hence we shouldn't be returning
        limited mocks only to attributes of the spec_set object.
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
        return unittest.mock.Mock(**kwargs)
