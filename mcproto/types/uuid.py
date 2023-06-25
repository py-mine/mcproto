from __future__ import annotations

import uuid
from typing import final

from typing_extensions import Self, override

from mcproto.buffer import Buffer
from mcproto.types.abc import MCType

__all__ = ["UUID"]


@final
class UUID(MCType, uuid.UUID):
    """Minecraft UUID type.

    In order to support potential future changes in protocol version, and implement McType,
    this is a custom subclass, however it is currently compatible with the stdlib's `uuid.UUID`.
    """

    __slots__ = ()

    @override
    def serialize(self) -> Buffer:
        buf = Buffer()
        buf.write(self.bytes)
        return buf

    @override
    @classmethod
    def deserialize(cls, buf: Buffer, /) -> Self:
        return cls(bytes=bytes(buf.read(16)))
