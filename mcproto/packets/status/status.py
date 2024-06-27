from __future__ import annotations

import json
from typing import Any, ClassVar, final

from attrs import Attribute, define, field
from typing_extensions import Self, override

from mcproto.buffer import Buffer
from mcproto.packets.packet import ClientBoundPacket, GameState, ServerBoundPacket

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

    data: dict[str, Any] = field()

    @data.validator  # pyright: ignore
    def _validate_data(self, _: Attribute[dict[str, Any]], value: dict[str, Any]) -> None:
        """Dump the data as json to check if it's valid."""
        json.dumps(value)

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
