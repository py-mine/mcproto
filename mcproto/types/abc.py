from __future__ import annotations

from mcproto.utils.abc import Serializable, dataclass

__all__ = ["MCType", "dataclass"]  # That way we can import it from mcproto.types.abc


class MCType(Serializable):
    """Base class for a minecraft type structure."""

    __slots__ = ()
