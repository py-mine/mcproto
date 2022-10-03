from __future__ import annotations

from abc import ABC, abstractmethod
from typing import ClassVar, TYPE_CHECKING

from mcproto.buffer import Buffer

if TYPE_CHECKING:
    from typing_extensions import Self


class Packet(ABC):
    """Base class for all packets"""

    __slots__ = ()

    PACKET_ID: ClassVar[int]

    def __new__(cls: type[Self], *a, **kw) -> Self:
        """Enforce PAKCET_ID being set for each instance of concrete packet classes.

        This performs a similar check to what ABCs do, as it ensures that PACKET_ID
        class variable was defined on the class before allowing initialization. Note
        that this does not prevent creating subclasses without PACKET_ID defined, it
        just prevents creating class instances without it.
        """
        if not hasattr(cls, "PACKET_ID"):
            raise TypeError(f"Can't instantiate abstract {cls.__name__} class without defining PACKET_ID classvar.")

        return super().__new__(cls)

    @abstractmethod
    def serialize(self) -> Buffer:
        """Represent the packet as a transmittable sequence of bytes."""
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def deserialize(cls, data: Buffer) -> Self:
        """Construct the packet from it's received byte representation."""
        raise NotImplementedError
