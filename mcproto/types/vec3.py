from __future__ import annotations

import math

from typing import final
from typing_extensions import override

from mcproto.buffer import Buffer
from mcproto.protocol import StructFormat
from mcproto.types.abc import MCType
from attrs import define


@define
class Vec3(MCType):
    """Represents a 3D vector.

    :param x: The x component.
    :param y: The y component.
    :param z: The z component.
    """

    x: float
    y: float
    z: float

    @override
    def serialize_to(self, buf: Buffer) -> None:
        buf.write_value(StructFormat.FLOAT, self.x)
        buf.write_value(StructFormat.FLOAT, self.y)
        buf.write_value(StructFormat.FLOAT, self.z)

    @override
    @classmethod
    def deserialize(cls, buf: Buffer) -> Vec3:
        x = buf.read_value(StructFormat.FLOAT)
        y = buf.read_value(StructFormat.FLOAT)
        z = buf.read_value(StructFormat.FLOAT)
        return cls(x=x, y=y, z=z)

    def serialize_to_double(self, buf: Buffer) -> None:
        """Serialize the vector to a buffer using double precision.

        .. seealso:: :meth:`serialize_to`
        """
        buf.write_value(StructFormat.DOUBLE, self.x)
        buf.write_value(StructFormat.DOUBLE, self.y)
        buf.write_value(StructFormat.DOUBLE, self.z)

    @classmethod
    def deserialize_double(cls, buf: Buffer) -> Vec3:
        """Deserialize a vector from a buffer using double precision.

        .. seealso:: :meth:`deserialize`
        """
        x = buf.read_value(StructFormat.DOUBLE)
        y = buf.read_value(StructFormat.DOUBLE)
        z = buf.read_value(StructFormat.DOUBLE)
        return cls(x=x, y=y, z=z)

    @override
    def validate(self) -> None:
        """Validate the vector's components."""
        # Check that the components are floats or integers.
        if not all(isinstance(comp, (float, int)) for comp in (self.x, self.y, self.z)):  # type: ignore
            raise TypeError(f"Vector components must be floats or integers, got {self.x!r}, {self.y!r}, {self.z!r}")

        # Check that the components are finite (not NaN or inf)
        if any(not math.isfinite(comp) for comp in (self.x, self.y, self.z)):
            raise ValueError(f"Vector components must be finite, got {self.x!r}, {self.y!r}, {self.z!r}.")

    def __add__(self, other: Vec3) -> Vec3:
        # Use the type of self to return a Vec3 or a subclass.
        return type(self)(x=self.x + other.x, y=self.y + other.y, z=self.z + other.z)

    def __sub__(self, other: Vec3) -> Vec3:
        return type(self)(x=self.x - other.x, y=self.y - other.y, z=self.z - other.z)

    def __neg__(self) -> Vec3:
        return type(self)(x=-self.x, y=-self.y, z=-self.z)

    def __mul__(self, other: float) -> Vec3:
        return type(self)(x=self.x * other, y=self.y * other, z=self.z * other)

    def __truediv__(self, other: float) -> Vec3:
        return type(self)(x=self.x / other, y=self.y / other, z=self.z / other)

    def to_position(self) -> Position:
        """Convert the vector to a position."""
        return Position(x=int(self.x), y=int(self.y), z=int(self.z))

    def to_tuple(self) -> tuple[float, float, float]:
        """Convert the vector to a tuple."""
        return (self.x, self.y, self.z)

    def to_vec3(self) -> Vec3:
        """Convert the vector to a Vec3.

        This function creates a new Vec3 object with the same components.
        """
        return Vec3(x=self.x, y=self.y, z=self.z)

    def norm_squared(self) -> float:
        """Return the squared norm of the vector."""
        return self.x**2 + self.y**2 + self.z**2

    def norm(self) -> float:
        """Return the norm of the vector."""
        return math.sqrt(self.norm_squared())

    def normalize(self) -> Vec3:
        """Return the normalized vector."""
        norm = self.norm()
        return Vec3(x=self.x / norm, y=self.y / norm, z=self.z / norm)


@final
class Position(Vec3):
    """Represents a position in the world.

    :param x: The x coordinate (26 bits).
    :param y: The y coordinate (12 bits).
    :param z: The z coordinate (26 bits).
    """

    x: int
    y: int
    z: int

    __slots__ = ()

    @override
    def serialize_to(self, buf: Buffer) -> None:
        encoded = ((self.x & 0x3FFFFFF) << 38) | ((self.z & 0x3FFFFFF) << 12) | (self.y & 0xFFF)

        # Convert the bit mess to a signed integer for packing.
        if encoded & 0x8000000000000000:
            encoded -= 1 << 64
        buf.write_value(StructFormat.LONGLONG, encoded)

    @override
    @classmethod
    def deserialize(cls, buf: Buffer) -> Position:
        encoded = buf.read_value(StructFormat.LONGLONG)
        x = (encoded >> 38) & 0x3FFFFFF
        z = (encoded >> 12) & 0x3FFFFFF
        y = encoded & 0xFFF

        # Convert back to signed integers.
        if x >= 1 << 25:
            x -= 1 << 26
        if y >= 1 << 11:
            y -= 1 << 12
        if z >= 1 << 25:
            z -= 1 << 26

        return cls(x=x, y=y, z=z)

    @override
    def validate(self) -> None:
        """Validate the position's coordinates.

        They are all signed integers, but the x and z coordinates are 26 bits
        and the y coordinate is 12 bits.
        """
        super().validate()  # Validate the Vec3 components.

        self.x = int(self.x)  # type: ignore
        self.y = int(self.y)  # type: ignore
        self.z = int(self.z)  # type: ignore
        if not (-1 << 25 <= self.x < 1 << 25):
            raise OverflowError(f"Invalid x coordinate: {self.x}")
        if not (-1 << 11 <= self.y < 1 << 11):
            raise OverflowError(f"Invalid y coordinate: {self.y}")
        if not (-1 << 25 <= self.z < 1 << 25):
            raise OverflowError(f"Invalid z coordinate: {self.z}")


POS_UP = Position(0, 1, 0)
POS_DOWN = Position(0, -1, 0)
POS_NORTH = Position(0, 0, -1)
POS_SOUTH = Position(0, 0, 1)
POS_EAST = Position(1, 0, 0)
POS_WEST = Position(-1, 0, 0)

POS_ZERO = Position(0, 0, 0)
