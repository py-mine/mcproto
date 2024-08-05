from __future__ import annotations

import math
from typing import final

from attrs import Attribute, define, field, validators
from typing_extensions import override

from mcproto.buffer import Buffer
from mcproto.protocol import StructFormat
from mcproto.types.abc import MCType


@define
@final
class Quaternion(MCType):
    """Represents a quaternion.

    :param x: The x component.
    :param y: The y component.
    :param z: The z component.
    :param w: The w component.
    """

    @staticmethod
    def finite_validator(instance: Quaternion, attribute: Attribute[float], value: float) -> None:
        """Validate that the quaternion components are finite."""
        if not math.isfinite(value):
            raise ValueError(f"Quaternion components must be finite, got {value!r}")

    x: float = field(validator=[validators.instance_of((float, int)), finite_validator.__get__(object)])
    y: float = field(validator=[validators.instance_of((float, int)), finite_validator.__get__(object)])
    z: float = field(validator=[validators.instance_of((float, int)), finite_validator.__get__(object)])
    w: float = field(validator=[validators.instance_of((float, int)), finite_validator.__get__(object)])

    @override
    def serialize_to(self, buf: Buffer) -> None:
        buf.write_value(StructFormat.FLOAT, self.x)
        buf.write_value(StructFormat.FLOAT, self.y)
        buf.write_value(StructFormat.FLOAT, self.z)
        buf.write_value(StructFormat.FLOAT, self.w)

    @override
    @classmethod
    def deserialize(cls, buf: Buffer) -> Quaternion:
        x = buf.read_value(StructFormat.FLOAT)
        y = buf.read_value(StructFormat.FLOAT)
        z = buf.read_value(StructFormat.FLOAT)
        w = buf.read_value(StructFormat.FLOAT)
        return cls(x=x, y=y, z=z, w=w)

    def __add__(self, other: Quaternion) -> Quaternion:
        # Use the type of self to return a Quaternion or a subclass.
        return type(self)(x=self.x + other.x, y=self.y + other.y, z=self.z + other.z, w=self.w + other.w)

    def __sub__(self, other: Quaternion) -> Quaternion:
        return type(self)(x=self.x - other.x, y=self.y - other.y, z=self.z - other.z, w=self.w - other.w)

    def __neg__(self) -> Quaternion:
        return type(self)(x=-self.x, y=-self.y, z=-self.z, w=-self.w)

    def __mul__(self, other: float) -> Quaternion:
        return type(self)(x=self.x * other, y=self.y * other, z=self.z * other, w=self.w * other)

    def __truediv__(self, other: float) -> Quaternion:
        return type(self)(x=self.x / other, y=self.y / other, z=self.z / other, w=self.w / other)

    def to_tuple(self) -> tuple[float, float, float, float]:
        """Convert the quaternion to a tuple."""
        return (self.x, self.y, self.z, self.w)

    def norm_squared(self) -> float:
        """Return the squared norm of the quaternion."""
        return self.x**2 + self.y**2 + self.z**2 + self.w**2

    def norm(self) -> float:
        """Return the norm of the quaternion."""
        return math.sqrt(self.norm_squared())

    def normalize(self) -> Quaternion:
        """Return the normalized quaternion."""
        norm = self.norm()
        return Quaternion(x=self.x / norm, y=self.y / norm, z=self.z / norm, w=self.w / norm)
