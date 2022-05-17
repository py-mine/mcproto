from __future__ import annotations

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

        return inner

    return wrapper
