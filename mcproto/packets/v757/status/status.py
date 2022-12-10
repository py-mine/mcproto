from __future__ import annotations

import json
from typing import Any, ClassVar, TYPE_CHECKING

from mcproto.buffer import Buffer
from mcproto.packets.abc import ClientBoundPacket, GameState, ServerBoundPacket

if TYPE_CHECKING:
    from typing_extensions import Self

__all__ = ["StatusRequest", "StatusResponse"]


class StatusRequest(ServerBoundPacket):
    """Request from the client to get information on the server. (Client -> Server)"""

    __slots__ = ()

    PACKET_ID: ClassVar[int] = 0x00
    GAME_STATE: ClassVar[GameState] = GameState.STATUS

    def serialize(self) -> Buffer:
        return Buffer()

    @classmethod
    def deserialize(cls, buf: Buffer, /) -> Self:
        return cls()


class StatusResponse(ClientBoundPacket):
    """Response from the server to requesting client with status data information. (Server -> Client)

    :param dict[str, Any] data: JSON response data sent back to the client.
    """

    __slots__ = ("data",)

    PACKET_ID: ClassVar[int] = 0x00
    GAME_STATE: ClassVar[GameState] = GameState.STATUS

    def __init__(self, data: dict[str, Any]):
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
