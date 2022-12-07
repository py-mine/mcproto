from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from enum import IntEnum
from typing import ClassVar, TYPE_CHECKING

from mcproto.buffer import Buffer
from mcproto.utils.abc import RequiredParamsABCMixin

if TYPE_CHECKING:
    from typing_extensions import Self


__all__ = [
    "GameState",
    "Packet",
    "ServerBoundPacket",
    "ClientBoundPacket",
]


class GameState(IntEnum):
    HANDSHAKING = 0
    STATUS = 1
    LOGIN = 2
    PLAY = 3


class Packet(ABC, RequiredParamsABCMixin):
    """Base class for all packets"""

    _REQUIRRED_CLASS_VARS: ClassVar[Sequence[str]] = ["PACKET_ID", "GAME_STATE"]
    _REQUIRED_CLASS_VARS_NO_MRO: ClassVar[Sequence[str]] = ["__slots__"]

    __slots__ = ()

    PACKET_ID: ClassVar[int]
    GAME_STATE: ClassVar[GameState]

    @abstractmethod
    def serialize(self) -> Buffer:
        """Represent the packet as a transmittable sequence of bytes."""
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def deserialize(cls, buf: Buffer, /) -> Self:
        """Construct the packet from it's received byte representation."""
        raise NotImplementedError


class ServerBoundPacket(Packet):
    """Packet bound to a server (Client -> Server)."""


class ClientBoundPacket(Packet):
    """Packet bound to a client (Server -> Client)."""
