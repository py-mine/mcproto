from __future__ import annotations

from collections.abc import Sequence
from enum import IntEnum
from typing import ClassVar

from mcproto.utils.abc import RequiredParamsABCMixin, Serializable

__all__ = [
    "GameState",
    "PacketDirection",
    "Packet",
    "ServerBoundPacket",
    "ClientBoundPacket",
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


class Packet(Serializable, RequiredParamsABCMixin):
    """Base class for all packets."""

    _REQUIRED_CLASS_VARS: ClassVar[Sequence[str]] = ["PACKET_ID", "GAME_STATE"]
    _REQUIRED_CLASS_VARS_NO_MRO: ClassVar[Sequence[str]] = ["__slots__"]

    __slots__ = ()

    PACKET_ID: ClassVar[int]
    GAME_STATE: ClassVar[GameState]


class ServerBoundPacket(Packet):
    """Packet bound to a server (Client -> Server)."""

    __slots__ = ()


class ClientBoundPacket(Packet):
    """Packet bound to a client (Server -> Client)."""

    __slots__ = ()
