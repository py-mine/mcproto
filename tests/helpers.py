from __future__ import annotations

import asyncio
import inspect
from typing import Any, Callable, Coroutine, TYPE_CHECKING, TypeVar

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
    However it isn't useful in production, since will cause typing issues (attributes will be accesssible, but
    type checkers won't know that they exist here, because of the dynamic nature of this implementation).
    """

    _WRAPPED_ATTRIBUTE: str

    def __getattribute__(self, __name: str) -> Any:
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
        try:
            wrapped = getattr(self, self._WRAPPED_ATTRIBUTE)
        except AttributeError:
            return super().__setattr__(__name, __value)
        else:
            if hasattr(wrapped, __name):
                return setattr(wrapped, __name, __value)

        return super().__setattr__(__name, __value)
