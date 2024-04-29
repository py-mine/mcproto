from __future__ import annotations

import json
from typing import Any, ClassVar, final

from typing_extensions import Self

from mcproto.buffer import Buffer
from mcproto.packets.packet import ClientBoundPacket, GameState, ServerBoundPacket
from mcproto.utils.abc import dataclass

__all__ = ["StatusRequest", "StatusResponse"]


@final
@dataclass
class StatusRequest(ServerBoundPacket):
    """Request from the client to get information on the server. (Client -> Server)."""

    PACKET_ID: ClassVar[int] = 0x00
    GAME_STATE: ClassVar[GameState] = GameState.STATUS

    def serialize_to(self, buf: Buffer) -> None:
        """Serialize the packet."""
        ...  # pragma: no cover, nothing to test here.

    @classmethod
    def _deserialize(cls, buf: Buffer, /) -> Self:  # pragma: no cover, nothing to test here.
        """Deserialize the packet."""
        return cls()


@final
@dataclass
class StatusResponse(ClientBoundPacket):
    """Response from the server to requesting client with status data information. (Server -> Client).

    Initialize the StatusResponse packet.

    :param data: JSON response data sent back to the client.
    """

    PACKET_ID: ClassVar[int] = 0x00
    GAME_STATE: ClassVar[GameState] = GameState.STATUS

    data: dict[str, Any]  # JSON response data sent back to the client.

    def serialize_to(self, buf: Buffer) -> None:
        """Serialize the packet."""
        s = json.dumps(self.data)
        buf.write_utf(s)

    @classmethod
    def _deserialize(cls, buf: Buffer, /) -> Self:
        """Deserialize the packet."""
        s = buf.read_utf()
        data_ = json.loads(s)
        return cls(data_)

    def validate(self) -> None:
        """Validate the packet data."""
        # Ensure the data is serializable to JSON
        try:
            json.dumps(self.data)
        except TypeError as exc:
            raise ValueError("Data is not serializable to JSON.") from exc
