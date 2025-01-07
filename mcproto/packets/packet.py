from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from enum import IntEnum
from typing import ClassVar

from typing_extensions import Self, override

from mcproto.buffer import Buffer
from mcproto.utils.abc import RequiredParamsABCMixin, Serializable

__all__ = [
    "ClientBoundPacket",
    "GameState",
    "Packet",
    "PacketDirection",
    "ServerBoundPacket",
]


class GameState(IntEnum):
    """All possible game states in minecraft."""

    HANDSHAKING = 0
    STATUS = 1
    LOGIN = 2
    PLAY = 3


class PacketDirection(IntEnum):
    """Represents whether a packet targets (is bound to) a client or server."""

    SERVERBOUND = 0
    CLIENTBOUND = 1


class Packet(Serializable, RequiredParamsABCMixin, ABC):
    """Base class for all packets."""

    _REQUIRED_CLASS_VARS: ClassVar[Sequence[str]] = ["PACKET_ID", "GAME_STATE"]
    _REQUIRED_CLASS_VARS_NO_MRO: ClassVar[Sequence[str]] = ["__slots__"]

    __slots__ = ()

    PACKET_ID: ClassVar[int]
    GAME_STATE: ClassVar[GameState]

    @override
    @classmethod
    def deserialize(cls, buf: Buffer, /) -> Self:
        try:
            return cls._deserialize(buf)
        except IOError as exc:
            raise InvalidPacketContentError.from_packet_class(cls, buf, repr(exc)) from exc

    @classmethod
    @abstractmethod
    def _deserialize(cls, buf: Buffer, /) -> Self:
        raise NotImplementedError


class ServerBoundPacket(Packet, ABC):
    """Packet bound to a server (Client -> Server)."""

    __slots__ = ()


class ClientBoundPacket(Packet, ABC):
    """Packet bound to a client (Server -> Client)."""

    __slots__ = ()


class InvalidPacketContentError(IOError):
    """Unable to deserialize given packet, as it didn't match the expected content.

    This error can occur during deserialization of a specific packet (after the
    packet class was already identified), but the deserialization process for this
    packet type failed.

    This can happen if the server sent a known packet, but it's content didn't match
    the expected content for this packet kind.
    """

    def __init__(
        self,
        packet_id: int,
        game_state: GameState,
        direction: PacketDirection,
        buffer: Buffer,
        message: str,
    ) -> None:
        """Initialize the error class.

        :param packet_id: Identified packet ID.
        :param game_state: Game state of the identified packet.
        :param direction: Packet direction of the identified packet.
        :param buffer: Buffer received for deserialization, that failed to parse.
        :param message: Reason for the failure.
        """
        self.packet_id = packet_id
        self.game_state = game_state
        self.direction = direction
        self.buffer = buffer
        self.message = message
        super().__init__(self.msg)

    @classmethod
    def from_packet_class(cls, packet_class: type[Packet], buffer: Buffer, message: str) -> Self:
        """Construct the error from packet class.

        This is a convenience constructor, picking up the necessary parameters about the identified packet
        from the packet class automatically (packet id, game state, ...).
        """
        if issubclass(packet_class, ServerBoundPacket):
            direction = PacketDirection.SERVERBOUND
        elif issubclass(packet_class, ClientBoundPacket):
            direction = PacketDirection.CLIENTBOUND
        else:
            raise TypeError(
                "Unable to determine the packet direction. Got a packet class which doesn't "
                "inherit from ServerBoundPacket nor ClientBoundPacket class."
            )

        return cls(packet_class.PACKET_ID, packet_class.GAME_STATE, direction, buffer, message)

    @property
    def msg(self) -> str:
        """Produce a message for this error."""
        msg_parts = []

        if self.direction is PacketDirection.CLIENTBOUND:
            msg_parts.append("Clientbound")
        else:
            msg_parts.append("Serverbound")

        msg_parts.append("packet in")

        if self.game_state is GameState.HANDSHAKING:
            msg_parts.append("handshaking")
        elif self.game_state is GameState.STATUS:
            msg_parts.append("status")
        elif self.game_state is GameState.LOGIN:
            msg_parts.append("login")
        else:
            msg_parts.append("play")

        msg_parts.append("game state")
        msg_parts.append(f"with ID: 0x{self.packet_id:02x}")
        msg_parts.append(f"failed to deserialize: {self.message}")

        return " ".join(msg_parts)

    @override
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.msg})"
