from __future__ import annotations

from abc import ABC, abstractmethod
from enum import IntEnum
from typing import ClassVar, TYPE_CHECKING

from mcproto.buffer import Buffer

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


class Packet(ABC):
    """Base class for all packets"""

    __slots__ = ()

    PACKET_ID: ClassVar[int]
    GAME_STATE: ClassVar[GameState]

    def __new__(cls: type[Self], *a, **kw) -> Self:
        """Enforce required parameters being set for each instance of concrete packet classes.

        This performs a similar check to what ABCs do, as it ensures that some required
        class variables were defined on the class before allowing initialization. Note
        that this does not prevent creating subclasses without these defined, it just
        prevents the creation of new instances on classes without it.
        """
        _err_msg = f"Can't instantiate abstract {cls.__name__} class without defining " + "{!r} classvar"
        if not hasattr(cls, "PACKET_ID"):
            raise TypeError(_err_msg.format("PACKET_ID"))
        if not hasattr(cls, "GAME_STATE"):
            raise TypeError(_err_msg.format("GAME_STATE"))

        return super().__new__(cls)

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
