from __future__ import annotations

from typing import ClassVar, TYPE_CHECKING

from mcproto.buffer import Buffer
from mcproto.packets.abc import ClientBoundPacket, GameState, ServerBoundPacket
from mcproto.protocol.base_io import StructFormat

if TYPE_CHECKING:
    from typing_extensions import Self


__all__ = ["PingPong"]


class PingPong(ClientBoundPacket, ServerBoundPacket):
    """Ping request/Pong response (Server <-> Client).

    :param int payload: Random number to test out the connection (ideally a long one).
    """

    __slots__ = ("payload",)

    PACKET_ID: ClassVar[int] = 0x01
    GAME_STATE: ClassVar[GameState] = GameState.STATUS

    def __init__(self, payload: int):
        self.payload = payload

    def serialize(self) -> Buffer:
        buf = Buffer()
        buf.write_value(StructFormat.LONGLONG, self.payload)
        return buf

    @classmethod
    def deserialize(cls, buf: Buffer, /) -> Self:
        payload = buf.read_value(StructFormat.LONGLONG)
        return cls(payload)
