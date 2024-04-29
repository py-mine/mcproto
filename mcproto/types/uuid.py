from __future__ import annotations

import uuid
from typing import final

from typing_extensions import Self

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

    def serialize_to(self, buf: Buffer) -> None:
        """Write the UUID to a buffer.

        :param buf: Buffer to write the UUID to.
        """
        buf.write(self.bytes)

    @classmethod
    def deserialize(cls, buf: Buffer, /) -> Self:
        """Deserialize a UUID from a buffer.

        :param buf: Buffer to read the UUID from.
        """
        data = bytes(buf.read(16))
        return cls(bytes=data)

    def validate(self) -> None:
        """No validation is required for UUIDs."""
        return
