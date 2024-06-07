from __future__ import annotations

from typing import ClassVar, final

from typing_extensions import Self, override

from mcproto.buffer import Buffer
from mcproto.packets.packet import ClientBoundPacket, GameState, ServerBoundPacket
from mcproto.protocol.base_io import StructFormat
from attrs import define

__all__ = ["PingPong"]


@final
@define
class PingPong(ClientBoundPacket, ServerBoundPacket):
    """Ping request/Pong response (Server <-> Client).

    Initialize the PingPong packet.

    :param payload:
        Random number to test out the connection. Ideally, this number should be quite big,
        however it does need to fit within the limit of a signed long long (-2 ** 63 to 2 ** 63 - 1).
    """

    PACKET_ID: ClassVar[int] = 0x01
    GAME_STATE: ClassVar[GameState] = GameState.STATUS

    payload: int

    @override
    def serialize_to(self, buf: Buffer) -> None:
        buf.write_value(StructFormat.LONGLONG, self.payload)

    @override
    @classmethod
    def _deserialize(cls, buf: Buffer, /) -> Self:
        payload = buf.read_value(StructFormat.LONGLONG)
        return cls(payload)
