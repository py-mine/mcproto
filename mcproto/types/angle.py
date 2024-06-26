from __future__ import annotations

import math
from typing import final

from attrs import define, field
from typing_extensions import override

from mcproto.buffer import Buffer
from mcproto.protocol import StructFormat
from mcproto.types.abc import MCType
from mcproto.types.vec3 import Vec3


@final
@define
class Angle(MCType):
    """Represents a rotation angle for an entity.

    :param value: The angle value in 1/256th of a full rotation.
    :type value: int

    .. note:: The angle is stored as a byte, so the value is in the range [0, 255].
    """

    angle: int = field(converter=lambda x: int(x) % 256)

    @override
    def serialize_to(self, buf: Buffer) -> None:
        payload = int(self.angle) & 0xFF
        # Convert to a signed byte.
        if payload & 0x80:
            payload -= 1 << 8
        buf.write_value(StructFormat.BYTE, payload)

    @override
    @classmethod
    def deserialize(cls, buf: Buffer) -> Angle:
        payload = buf.read_value(StructFormat.BYTE)
        return cls(angle=int(payload * 360 / 256))

    def in_direction(self, base: Vec3, distance: float) -> Vec3:
        """Calculate the position in the direction of the angle in the xz-plane.

        0/256: Positive z-axis
        64/-192: Negative x-axis
        128/-128: Negative z-axis
        192/-64: Positive x-axis

        :param base: The base position.
        :param distance: The distance to move.
        :return: The new position.
        """
        x = base.x - distance * math.sin(self.to_radians())
        z = base.z + distance * math.cos(self.to_radians())
        return Vec3(x=x, y=base.y, z=z)

    @classmethod
    def from_degrees(cls, degrees: float) -> Angle:
        """Create an angle from degrees."""
        return cls(angle=int(degrees * 256 / 360))

    def to_degrees(self) -> float:
        """Return the angle in degrees."""
        return self.angle * 360 / 256

    @classmethod
    def from_radians(cls, radians: float) -> Angle:
        """Create an angle from radians."""
        return cls(angle=int(math.degrees(radians) * 256 / 360))

    def to_radians(self) -> float:
        """Return the angle in radians."""
        return math.radians(self.angle * 360 / 256)
