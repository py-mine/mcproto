from __future__ import annotations

import inspect
from functools import wraps
from typing import Callable, Optional, TYPE_CHECKING, TypeVar, cast

if TYPE_CHECKING:
    from typing_extensions import ParamSpec

    P = ParamSpec("P")

R = TypeVar("R")


def enforce_range(*, typ: str, byte_size: Optional[int], signed: bool) -> Callable:
    """Decorator enforcing proper int value range, based on the number of bytes.

    If a value is outside of the automatically determined allowed range, a ValueError will be raised,
    showing the given `typ` along with the allowed range info.

    If the byte_size is None, infinite max size is assumed. Note that this is only possible with unsigned types,
    since there's no point in enforcing infinite range.
    """
    if byte_size is None:
        if signed is True:
            raise ValueError("Enforcing infinite byte-size for signed type doesn't make sense (includes all numbers).")
        value_max = float("inf")
        value_max_s = "infinity"
        value_min = 0
        value_min_s = "0"
    else:
        if signed:
            value_max = (1 << (byte_size * 8 - 1)) - 1
            value_max_s = f"{value_max} (2**{byte_size * 8 - 1} - 1)"
            value_min = -1 << (byte_size * 8 - 1)
            value_min_s = f"{value_min} (-2**{byte_size * 8 - 1})"
        else:
            value_max = (1 << (byte_size * 8)) - 1
            value_max_s = f"{value_max} (2**{byte_size * 8} - 1)"
            value_min = 0
            value_min_s = "0"

    def wrapper(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def inner(*args: P.args, **kwargs: P.kwargs) -> R:
            value = cast(int, args[1])
            if value > value_max or value < value_min:
                raise ValueError(f"{typ} must be within {value_min_s} and {value_max_s}, got {value}.")
            return func(*args, **kwargs)

        @wraps(func)
        async def async_inner(*args: P.args, **kwargs: P.kwargs) -> R:
            value = cast(int, args[1])
            if value > value_max or value < value_min:
                raise ValueError(f"{typ} must be within {value_min_s} and {value_max_s}, got {value}.")
            return await func(*args, **kwargs)  # type: ignore

        # We technically don't need async version of inner here, and instead just call the function,
        # even if it's async, since it will simply produce a coroutine which can be then awaited by the user.
        #
        # However doing this can produce some unexpected behavior for the user, such as the decorated function
        # now becoming synchronous, and only returning a coroutine object, instead of actually being asynchronous.
        # This usually doesn't matter, since these act the same, however it does mean that for example using
        # `inspect.iscoroutinefunction` would produce False, even though the wrapped function still does return
        # a coroutine, because the `inner` function it now became is actually synchronous.
        #
        # Our tests currently rely on this inspect function working properly, even for decorated methods,
        # which requires us to do this properly and use both sync and async `inner` alternatives.
        if inspect.iscoroutinefunction(func):
            return async_inner  # type: ignore
        return inner

    return wrapper
