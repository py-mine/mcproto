from __future__ import annotations

import json
from typing import Any, ClassVar, final

from typing_extensions import Self

from mcproto.buffer import Buffer
from mcproto.packets.abc import ClientBoundPacket, GameState, ServerBoundPacket

__all__ = ["StatusRequest", "StatusResponse"]


@final
class StatusRequest(ServerBoundPacket):
    """Request from the client to get information on the server. (Client -> Server)"""

    __slots__ = ()

    PACKET_ID: ClassVar[int] = 0x00
    GAME_STATE: ClassVar[GameState] = GameState.STATUS

    def serialize(self) -> Buffer:  # pragma: no cover, nothing to test here.
        return Buffer()

    @classmethod
    def deserialize(cls, buf: Buffer, /) -> Self:  # pragma: no cover, nothing to test here.
        return cls()


@final
class StatusResponse(ClientBoundPacket):
    """Response from the server to requesting client with status data information. (Server -> Client)"""

    __slots__ = ("data",)

    PACKET_ID: ClassVar[int] = 0x00
    GAME_STATE: ClassVar[GameState] = GameState.STATUS

    def __init__(self, data: dict[str, Any]):
        """
        :param data: JSON response data sent back to the client.
        """
        self.data = data

    def serialize(self) -> Buffer:
        buf = Buffer()
        s = json.dumps(self.data)
        buf.write_utf(s)
        return buf

    @classmethod
    def deserialize(cls, buf: Buffer, /) -> Self:
        s = buf.read_utf()
        data_ = json.loads(s)
        return cls(data_)
