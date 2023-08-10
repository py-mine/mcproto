from __future__ import annotations

from enum import IntEnum
from typing import ClassVar, final

from typing_extensions import Self

from mcproto.buffer import Buffer
from mcproto.packets.packet import GameState, ServerBoundPacket
from mcproto.protocol.base_io import StructFormat

__all__ = [
    "NextState",
    "Handshake",
]


class NextState(IntEnum):
    """Enum of all possible next game states we can transition to from the :class:`Handshake` packet."""

    STATUS = 1
    LOGIN = 2


@final
class Handshake(ServerBoundPacket):
    """Initializes connection between server and client. (Client -> Server)."""

    PACKET_ID: ClassVar[int] = 0x00
    GAME_STATE: ClassVar[GameState] = GameState.HANDSHAKING

    __slots__ = ("protocol_version", "server_address", "server_port", "next_state")

    def __init__(
        self,
        *,
        protocol_version: int,
        server_address: str,
        server_port: int,
        next_state: NextState | int,
    ):
        """Initialize the Handshake packet.

        :param protocol_version: Protocol version number to be used.
        :param server_address: The host/address the client is connecting to.
        :param server_port: The port the client is connecting to.
        :param next_state: The next state for the server to move into.
        """
        if not isinstance(next_state, NextState):  # next_state is int
            rev_lookup = {x.value: x for x in NextState.__members__.values()}
            try:
                next_state = rev_lookup[next_state]
            except KeyError as exc:
                raise ValueError("No such next_state.") from exc

        self.protocol_version = protocol_version
        self.server_address = server_address
        self.server_port = server_port
        self.next_state = next_state

    def serialize(self) -> Buffer:
        """Serialize the packet."""
        buf = Buffer()
        buf.write_varint(self.protocol_version)
        buf.write_utf(self.server_address)
        buf.write_value(StructFormat.USHORT, self.server_port)
        buf.write_varint(self.next_state.value)
        return buf

    @classmethod
    def deserialize(cls, buf: Buffer, /) -> Self:
        """Deserialize the packet."""
        return cls(
            protocol_version=buf.read_varint(),
            server_address=buf.read_utf(),
            server_port=buf.read_value(StructFormat.USHORT),
            next_state=buf.read_varint(),
        )
