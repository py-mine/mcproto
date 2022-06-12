from __future__ import annotations

import inspect
import warnings
from functools import wraps
from typing import Callable, Iterable, Optional, TYPE_CHECKING, Type, TypeVar, Union, cast, overload

if TYPE_CHECKING:
    from typing_extensions import ParamSpec, Protocol

    P = ParamSpec("P")
    P2 = ParamSpec("P2")
else:
    Protocol = object

T = TypeVar("T")
R = TypeVar("R")
R2 = TypeVar("R2")


class DeprecatedReturn(Protocol):
    @overload
    def __call__(self, __x: Type[T]) -> Type[T]:
        ...

    @overload
    def __call__(self, __x: Callable[P, R]) -> Callable[P, R]:
        ...


@overload
def deprecated(
    obj: Callable[P, R],
    *,
    display_name: Optional[str] = None,
    replacement: Optional[str] = None,
    version: Optional[str] = None,
    date: Optional[str] = None,
    msg: Optional[str] = None,
) -> Callable[P, R]:
    ...


@overload
def deprecated(
    obj: Type[T],
    *,
    display_name: Optional[str] = None,
    replacement: Optional[str] = None,
    version: Optional[str] = None,
    date: Optional[str] = None,
    msg: Optional[str] = None,
    methods: Iterable[str],
) -> Type[T]:
    ...


@overload
def deprecated(
    obj: None = None,
    *,
    display_name: Optional[str] = None,
    replacement: Optional[str] = None,
    version: Optional[str] = None,
    date: Optional[str] = None,
    msg: Optional[str] = None,
    methods: Optional[Iterable[str]] = None,
) -> DeprecatedReturn:
    ...


def deprecated(
    obj: Optional[Union[Callable, Type[object]]] = None,
    *,
    display_name: Optional[str] = None,
    replacement: Optional[str] = None,
    version: Optional[str] = None,
    date: Optional[str] = None,
    msg: Optional[str] = None,
    methods: Optional[Iterable[str]] = None,
) -> Callable:
    if date is not None and version is not None:
        raise ValueError("Expected removal timeframe can either be a date, or a version, not both.")

    def decorate_func(func: Callable[P2, R2], warn_message: str) -> Callable[P2, R2]:
        @wraps(func)
        def wrapper(*args: P2.args, **kwargs: P2.kwargs) -> R2:
            warnings.simplefilter("always", DeprecationWarning)
            warnings.warn(warn_message, category=DeprecationWarning)
            warnings.simplefilter("default", DeprecationWarning)
            return func(*args, **kwargs)

        return wrapper

    @overload
    def decorate(obj: Callable[P, R]) -> Callable[P, R]:
        ...

    @overload
    def decorate(obj: Type[T]) -> Type[T]:
        ...

    def decorate(obj: Union[Callable[P, R], Type[T]]) -> Union[Callable[P, R], Type[T]]:
        # Construct and send the warning message
        name = getattr(obj, "__qualname__", obj.__name__) if display_name is None else display_name
        warn_message = f"'{name}' is deprecated and is expected to be removed"
        if version is not None:
            warn_message += f" in {version}"
        elif date is not None:
            warn_message += f" on {date}"
        else:
            warn_message += " eventually"
        if replacement is not None:
            warn_message += f", use '{replacement}' instead"
        warn_message += "."
        if msg is not None:
            warn_message += f" ({msg})"

        # If we're deprecating class, deprecate it's methods and return the class
        if inspect.isclass(obj):
            obj = cast(Type[T], obj)

            if methods is None:
                raise ValueError("When deprecating a class, you need to specify 'methods' which will get the notice")

            for method in methods:
                new_func = decorate_func(getattr(obj, method), warn_message)
                setattr(obj, method, new_func)

            return obj

        # Regular function deprecation
        obj = cast(Callable[P, R], obj)
        if methods is not None:
            raise ValueError("Methods can only be specified when decorating a class, not a function")
        return decorate_func(obj, warn_message)

    # In case the decorator was used like @deprecated, instead of @deprecated()
    # we got the object already, pass it over to the local decorate function
    # This can happen since all of the arguments are optional and can be omitted
    if obj:
        return decorate(obj)
    return decorate
