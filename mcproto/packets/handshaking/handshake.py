from __future__ import annotations

from enum import IntEnum
from typing import ClassVar, cast, final

from typing_extensions import Self, override

from mcproto.buffer import Buffer
from mcproto.packets.packet import GameState, ServerBoundPacket
from mcproto.protocol.base_io import StructFormat
from mcproto.utils.abc import dataclass

__all__ = [
    "NextState",
    "Handshake",
]


class NextState(IntEnum):
    """Enum of all possible next game states we can transition to from the :class:`Handshake` packet."""

    STATUS = 1
    LOGIN = 2


@final
@dataclass
class Handshake(ServerBoundPacket):
    """Initializes connection between server and client. (Client -> Server).

    Initialize the Handshake packet.

    :param protocol_version: Protocol version number to be used.
    :param server_address: The host/address the client is connecting to.
    :param server_port: The port the client is connecting to.
    :param next_state: The next state for the server to move into.
    """

    PACKET_ID: ClassVar[int] = 0x00
    GAME_STATE: ClassVar[GameState] = GameState.HANDSHAKING

    protocol_version: int
    server_address: str
    server_port: int
    next_state: NextState | int

    @override
    def serialize_to(self, buf: Buffer) -> None:
        """Serialize the packet."""
        self.next_state = cast(NextState, self.next_state)  # Handled by the validate method
        buf.write_varint(self.protocol_version)
        buf.write_utf(self.server_address)
        buf.write_value(StructFormat.USHORT, self.server_port)
        buf.write_varint(self.next_state.value)

    @override
    @classmethod
    def _deserialize(cls, buf: Buffer, /) -> Self:
        return cls(
            protocol_version=buf.read_varint(),
            server_address=buf.read_utf(),
            server_port=buf.read_value(StructFormat.USHORT),
            next_state=buf.read_varint(),
        )

    @override
    def validate(self) -> None:
        """Validate the packet."""
        if not isinstance(self.next_state, NextState):
            rev_lookup = {x.value: x for x in NextState.__members__.values()}
            try:
                self.next_state = rev_lookup[self.next_state]
            except KeyError as exc:
                raise ValueError("No such next_state.") from exc
