from __future__ import annotations

import uuid
from typing import final

from typing_extensions import Self

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

    def serialize(self) -> Buffer:
        """Serialize the UUID."""
        buf = Buffer()
        buf.write(self.bytes)
        return buf

    @classmethod
    def deserialize(cls, buf: Buffer, /) -> Self:
        """Deserialize a UUID."""
        return cls(bytes=bytes(buf.read(16)))
