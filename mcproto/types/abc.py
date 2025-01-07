from __future__ import annotations

from abc import ABC

from mcproto.utils.abc import Serializable

__all__ = ["MCType"]


class MCType(Serializable, ABC):
    """Base class for a minecraft type structure."""

    __slots__ = ()
