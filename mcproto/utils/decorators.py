from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import Protocol, TypeVar

from typing_extensions import ParamSpec

__all__ = ["copied_return"]

T = TypeVar("T")


class SupportsCopy(Protocol):
    def copy(self: T) -> T:
        ...


P = ParamSpec("P")
R_Copyable = TypeVar("R_Copyable", bound=SupportsCopy)


def copied_return(func: Callable[P, R_Copyable]) -> Callable[P, R_Copyable]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R_Copyable:
        ret = func(*args, **kwargs)
        return ret.copy()

    return wrapper
