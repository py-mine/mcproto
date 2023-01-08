from __future__ import annotations

import importlib.metadata
import warnings
from collections.abc import Callable
from functools import wraps
from typing import Optional, TypeVar, Union

from typing_extensions import ParamSpec, Protocol

from mcproto.utils.version import SemanticVersion

__all__ = ["deprecated", "deprecation_warn"]

R = TypeVar("R")
P = ParamSpec("P")


def deprecation_warn(
    *,
    obj_name: str,
    removal_version: Union[str, SemanticVersion],
    replacement: Optional[str] = None,
    extra_msg: Optional[str] = None,
    stack_level: int = 3,
) -> None:
    """Produce an appropriate deprecation warning given the parameters.

    If the currently installed project version is already past the specified deprecation version,
    a DeprecationWarning will be raised as a full exception. Otherwise it will just get emitted
    as a warning.

    The deprecation message used will be constructed based on the input parameters.
    """
    if isinstance(removal_version, str):
        removal_version = SemanticVersion.from_string(removal_version)

    try:
        _project_version = importlib.metadata.version(__package__)
    except importlib.metadata.PackageNotFoundError:
        # v0.0.0 will never mark things as already deprecated (removal_version will always be newer)
        project_version = SemanticVersion((0, 0, 0))
    else:
        project_version = SemanticVersion.from_string(_project_version)

    already_deprecated = project_version >= removal_version

    msg = f"{obj_name!r}"
    if already_deprecated:
        msg += f" is passed its removal version ({removal_version})"
    else:
        msg += f" is deprecated and scheduled for removal in {removal_version}"

    if replacement is not None:
        msg += f", use '{replacement}' instead"

    msg += "."
    if extra_msg is not None:
        msg += f" ({extra_msg})"

    if already_deprecated:
        raise DeprecationWarning(msg)

    warnings.warn(msg, category=DeprecationWarning, stacklevel=stack_level)


class DecoratorFunction(Protocol):
    def __call__(self, __x: Callable[P, R]) -> Callable[P, R]:
        ...


def deprecated(
    removal_version: Union[str, SemanticVersion],
    display_name: Optional[str] = None,
    replacement: Optional[str] = None,
    extra_msg: Optional[str] = None,
) -> DecoratorFunction:
    """Mark an object as deprecated.

    Decorator version of ``deprecation_warn`` function.

    By default, the display name will be obtained from the decorated object (__qualname__), if this is not
    desired, you can specify the `display_name` attribute to override it.
    """

    def inner(func: Callable[P, R]) -> Callable[P, R]:
        obj_name = getattr(func, "__qualname__", func.__name__) if display_name is None else display_name

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            deprecation_warn(
                obj_name=obj_name,
                removal_version=removal_version,
                replacement=replacement,
                extra_msg=extra_msg,
                stack_level=3,
            )
            return func(*args, **kwargs)

        return wrapper

    return inner
