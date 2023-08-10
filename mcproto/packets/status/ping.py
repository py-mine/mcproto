from __future__ import annotations

from typing import ClassVar, final

from typing_extensions import Self

from mcproto.buffer import Buffer
from mcproto.packets.packet import ClientBoundPacket, GameState, ServerBoundPacket
from mcproto.protocol.base_io import StructFormat

__all__ = ["PingPong"]


@final
class PingPong(ClientBoundPacket, ServerBoundPacket):
    """Ping request/Pong response (Server <-> Client)."""

    __slots__ = ("payload",)

    PACKET_ID: ClassVar[int] = 0x01
    GAME_STATE: ClassVar[GameState] = GameState.STATUS

    def __init__(self, payload: int):
        """Initialize the PingPong packet.

        :param payload:
            Random number to test out the connection. Ideally, this number should be quite big,
            however it does need to fit within the limit of a signed long long (-2 ** 63 to 2 ** 63 - 1).
        """
        self.payload = payload

    def serialize(self) -> Buffer:
        """Serialize the packet."""
        buf = Buffer()
        buf.write_value(StructFormat.LONGLONG, self.payload)
        return buf

    @classmethod
    def deserialize(cls, buf: Buffer, /) -> Self:
        """Deserialize the packet."""
        payload = buf.read_value(StructFormat.LONGLONG)
        return cls(payload)
