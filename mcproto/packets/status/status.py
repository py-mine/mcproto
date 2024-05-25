from __future__ import annotations

import json
from typing import Any, ClassVar, final

from typing_extensions import Self, override

from mcproto.buffer import Buffer
from mcproto.packets.packet import ClientBoundPacket, GameState, ServerBoundPacket
from mcproto.utils.abc import define

__all__ = ["StatusRequest", "StatusResponse"]


@final
@define
class StatusRequest(ServerBoundPacket):
    """Request from the client to get information on the server. (Client -> Server)."""

    PACKET_ID: ClassVar[int] = 0x00
    GAME_STATE: ClassVar[GameState] = GameState.STATUS

    @override
    def serialize_to(self, buf: Buffer) -> None:
        return  # pragma: no cover, nothing to test here.

    @override
    @classmethod
    def _deserialize(cls, buf: Buffer, /) -> Self:  # pragma: no cover, nothing to test here.
        return cls()


@final
@define
class StatusResponse(ClientBoundPacket):
    """Response from the server to requesting client with status data information. (Server -> Client).

    Initialize the StatusResponse packet.

    :param data: JSON response data sent back to the client.
    """

    PACKET_ID: ClassVar[int] = 0x00
    GAME_STATE: ClassVar[GameState] = GameState.STATUS

    data: dict[str, Any]  # JSON response data sent back to the client.

    @override
    def serialize_to(self, buf: Buffer) -> None:
        s = json.dumps(self.data, separators=(",", ":"))
        buf.write_utf(s)

    @override
    @classmethod
    def _deserialize(cls, buf: Buffer, /) -> Self:
        s = buf.read_utf()
        data_ = json.loads(s)
        return cls(data_)

    @override
    def validate(self) -> None:
        # Ensure the data is serializable to JSON
        try:
            json.dumps(self.data)
        except TypeError as exc:
            raise ValueError("Data is not serializable to JSON.") from exc
