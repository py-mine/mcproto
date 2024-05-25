from __future__ import annotations

from mcproto.utils.abc import Serializable, define

__all__ = ["MCType", "define"]  # That way we can import it from mcproto.types.abc


class MCType(Serializable):
    """Base class for a minecraft type structure."""

    __slots__ = ()
