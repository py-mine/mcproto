from __future__ import annotations

import uuid
from typing import final

from typing_extensions import Self, override

from mcproto.buffer import Buffer
from mcproto.types.abc import MCType

__all__ = ["UUID"]


@final
class UUID(uuid.UUID, MCType):
    """Minecraft UUID type.

    In order to support potential future changes in protocol version, and implement McType,
    this is a custom subclass, however it is currently compatible with the stdlib's `uuid.UUID`.
    """

    __slots__ = ()

    @override
    def serialize_to(self, buf: Buffer) -> None:
        buf.write(self.bytes)

    @override
    @classmethod
    def deserialize(cls, buf: Buffer, /) -> Self:
        data = bytes(buf.read(16))
        return cls(bytes=data)
