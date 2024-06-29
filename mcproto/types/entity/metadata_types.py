from __future__ import annotations

from enum import IntEnum
from typing import Any, ClassVar

from typing_extensions import override

from mcproto.buffer import Buffer
from mcproto.protocol import StructFormat
from mcproto.types.chat import TextComponent
from mcproto.types.entity.enums import Direction, DragonPhase, Pose, SnifferState
from mcproto.types.entity.metadata import EntityMetadataEntry, ProxyEntityMetadataEntry
from mcproto.types.identifier import Identifier
from mcproto.types.nbt import NBTag
from mcproto.types.quaternion import Quaternion
from mcproto.types.slot import Slot
from mcproto.types.uuid import UUID
from mcproto.types.vec3 import Position, Vec3


class ByteEME(EntityMetadataEntry):
    """Represents a byte entry in an entity metadata list."""

    ENTRY_TYPE: ClassVar[int] = 0
    __slots__ = ()

    value: int

    @override
    def serialize_to(self, buf: Buffer) -> None:
        self._write_header(buf)
        buf.write_value(StructFormat.BYTE, self.value)

    @override
    @classmethod
    def read_value(cls, buf: Buffer) -> int:
        return buf.read_value(StructFormat.BYTE)

    @override
    def validate(self) -> None:
        if not -128 <= self.value <= 127:
            raise ValueError(f"Byte value {self.value} is out of range.")
        super().validate()


class Masked(ProxyEntityMetadataEntry):
    """Represents a masked entry in an entity metadata list."""

    __slots__ = ("mask",)

    def __init__(self, bound_entry: EntityMetadataEntry, *, mask: int):
        super().__init__(bound_entry)
        self.mask = mask

    @override
    def setter(self, value: int) -> None:
        bound = self.bound_entry.getter()
        # spread value over the mask
        for i in range(32):
            if self.mask & (1 << i):
                bound = (bound & ~(1 << i)) | ((value & 1) << i)
                value >>= 1
        self.bound_entry.setter(bound)

    @override
    def getter(self) -> int:
        # collect bits from the mask
        value = 0
        bound = self.bound_entry.getter()
        if bound == 0:  # Save 32 iterations of a useless loop
            return 0
        shift = 0
        for i in range(32):
            if self.mask & (1 << i):
                # Find the bit that is set and shift it back to the right position
                value |= (bound & (1 << i)) >> (i - shift)
                shift += 1
        return value


class VarIntEME(EntityMetadataEntry):
    """Represents a varint entry in an entity metadata list."""

    ENTRY_TYPE: ClassVar[int] = 1
    __slots__ = ()

    value: int

    @override
    def serialize_to(self, buf: Buffer) -> None:
        self._write_header(buf)
        buf.write_varint(self.value)

    @override
    @classmethod
    def read_value(cls, buf: Buffer) -> Any:
        return buf.read_varint()

    @override
    def validate(self) -> None:
        if not -(2**31) <= self.value < 2**31:
            raise ValueError(f"VarInt value {self.value} is out of range.")
        super().validate()


class _RegistryVarIntEME(VarIntEME):
    """Represents a varint entry that refereces a registry ID in an entity metadata list."""

    ENTRY_TYPE: ClassVar[int] = -1
    __slots__ = ()


class _VarIntEnumEME(EntityMetadataEntry):
    """Represents a varint entry that refereces an enum in an entity metadata list."""

    ENTRY_TYPE: ClassVar[int] = -1
    __slots__ = ()
    ENUM: ClassVar[type[IntEnum]] = None  # type: ignore

    value: IntEnum

    @override
    def serialize_to(self, buf: Buffer) -> None:
        self._write_header(buf)
        buf.write_varint(self.value.value)

    @override
    @classmethod
    def read_value(cls, buf: Buffer) -> IntEnum:
        value = buf.read_varint()
        try:
            value_enum = cls.ENUM(value)
        except ValueError as e:
            raise ValueError(f"Invalid value {value} for enum {cls.ENUM.__name__}.") from e
        return value_enum

    @override
    def validate(self) -> None:
        super().validate()
        try:
            self.ENUM(self.value)
        except ValueError as e:
            raise ValueError(f"Invalid value {self.value} for enum {self.ENUM.__name__}.") from e


class VarLongEME(EntityMetadataEntry):
    """Represents a varlong entry in an entity metadata list."""

    ENTRY_TYPE: ClassVar[int] = 2
    __slots__ = ()

    value: int

    @override
    def serialize_to(self, buf: Buffer) -> None:
        self._write_header(buf)
        buf.write_varlong(self.value)

    @override
    @classmethod
    def read_value(cls, buf: Buffer) -> int:
        return buf.read_varlong()

    @override
    def validate(self) -> None:
        if not -(2**63) <= self.value < 2**63:
            raise ValueError(f"VarLong value {self.value} is out of range.")
        super().validate()


class FloatEME(EntityMetadataEntry):
    """Represents a float entry in an entity metadata list."""

    ENTRY_TYPE: ClassVar[int] = 3
    __slots__ = ()

    value: float

    @override
    def serialize_to(self, buf: Buffer) -> None:
        self._write_header(buf)
        buf.write_value(StructFormat.FLOAT, self.value)

    @override
    @classmethod
    def read_value(cls, buf: Buffer) -> float:
        return buf.read_value(StructFormat.FLOAT)


class StringEME(EntityMetadataEntry):
    """Represents a string entry in an entity metadata list."""

    ENTRY_TYPE: ClassVar[int] = 4
    __slots__ = ()

    value: str

    @override
    def serialize_to(self, buf: Buffer) -> None:
        self._write_header(buf)
        buf.write_utf(self.value)

    @override
    @classmethod
    def read_value(cls, buf: Buffer) -> str:
        return buf.read_utf()

    @override
    def validate(self) -> None:
        if len(self.value) > 32767:
            raise ValueError(f"String value {self.value} is too long.")
        super().validate()


class TextComponentEME(EntityMetadataEntry):
    """Represents a text component entry in an entity metadata list."""

    ENTRY_TYPE: ClassVar[int] = 5
    __slots__ = ()

    value: TextComponent

    @override
    def serialize_to(self, buf: Buffer) -> None:
        self._write_header(buf)
        self.value.serialize_to(buf)

    @override
    @classmethod
    def read_value(cls, buf: Buffer) -> TextComponent:
        return TextComponent.deserialize(buf)


class OptTextComponentEME(EntityMetadataEntry):
    """Represents an optional text component entry in an entity metadata list."""

    ENTRY_TYPE: ClassVar[int] = 6
    __slots__ = ()

    value: TextComponent | None

    @override
    def serialize_to(self, buf: Buffer) -> None:
        self._write_header(buf)
        # We use the old python True == 1 trick to represent a boolean
        buf.write_value(StructFormat.BYTE, self.value is not None)
        if self.value is not None:
            self.value.serialize_to(buf)

    @override
    @classmethod
    def read_value(cls, buf: Buffer) -> TextComponent | None:
        present = buf.read_value(StructFormat.BYTE)
        if present:
            return TextComponent.deserialize(buf)
        return None


class SlotEME(EntityMetadataEntry):
    """Represents a slot entry in an entity metadata list."""

    ENTRY_TYPE: ClassVar[int] = 7
    __slots__ = ()

    value: Slot

    @override
    def serialize_to(self, buf: Buffer) -> None:
        self._write_header(buf)
        self.value.serialize_to(buf)

    @override
    @classmethod
    def read_value(cls, buf: Buffer) -> Slot:
        return Slot.deserialize(buf)


class BooleanEME(EntityMetadataEntry):
    """Represents a boolean entry in an entity metadata list."""

    ENTRY_TYPE: ClassVar[int] = 8
    __slots__ = ()

    value: bool

    @override
    def serialize_to(self, buf: Buffer) -> None:
        self._write_header(buf)
        buf.write_value(StructFormat.BYTE, self.value)

    @override
    @classmethod
    def read_value(cls, buf: Buffer) -> bool:
        return bool(buf.read_value(StructFormat.BYTE))


class RotationEME(EntityMetadataEntry):
    """Represents a rotation entry in an entity metadata list."""

    ENTRY_TYPE: ClassVar[int] = 9
    __slots__ = ()

    value: Vec3

    @override
    def serialize_to(self, buf: Buffer) -> None:
        self._write_header(buf)
        self.value.serialize_to(buf)

    @override
    @classmethod
    def read_value(cls, buf: Buffer) -> Vec3:
        return Vec3.deserialize(buf)


class PositionEME(EntityMetadataEntry):
    """Represents a position entry in an entity metadata list."""

    ENTRY_TYPE: ClassVar[int] = 10
    __slots__ = ()

    value: Position

    @override
    def serialize_to(self, buf: Buffer) -> None:
        self._write_header(buf)
        self.value.serialize_to(buf)

    @override
    @classmethod
    def read_value(cls, buf: Buffer) -> Position:
        return Position.deserialize(buf)


class OptPositionEME(EntityMetadataEntry):
    """Represents an optional position entry in an entity metadata list."""

    ENTRY_TYPE: ClassVar[int] = 11
    __slots__ = ()

    value: Position | None

    @override
    def serialize_to(self, buf: Buffer) -> None:
        self._write_header(buf)
        # We use the old python True == 1 trick to represent a boolean
        buf.write_value(StructFormat.BYTE, self.value is not None)
        if self.value is not None:
            self.value.serialize_to(buf)

    @override
    @classmethod
    def read_value(cls, buf: Buffer) -> Position | None:
        present = buf.read_value(StructFormat.BYTE)
        if present:
            return Position.deserialize(buf)
        return None


class DirectionEME(EntityMetadataEntry):
    """Represents a direction in the world."""

    ENTRY_TYPE: ClassVar[int] = 12
    __slots__ = ()

    value: Direction

    @override
    def serialize_to(self, buf: Buffer) -> None:
        self._write_header(buf)
        buf.write_value(StructFormat.BYTE, self.value)

    @override
    @classmethod
    def read_value(cls, buf: Buffer) -> Direction:
        return Direction(buf.read_value(StructFormat.BYTE))


class OptUUIDEME(EntityMetadataEntry):
    """Represents an optional UUID entry in an entity metadata list."""

    ENTRY_TYPE: ClassVar[int] = 13
    __slots__ = ()

    value: UUID | None

    @override
    def serialize_to(self, buf: Buffer) -> None:
        self._write_header(buf)
        # We use the old python True == 1 trick to represent a boolean
        buf.write_value(StructFormat.BYTE, self.value is not None)
        if self.value is not None:
            self.value.serialize_to(buf)

    @override
    @classmethod
    def read_value(cls, buf: Buffer) -> UUID | None:
        present = buf.read_value(StructFormat.BYTE)
        if present:
            return UUID.deserialize(buf)
        return None


class BlockStateEME(VarIntEME):
    """Represents a block state in the world."""

    ENTRY_TYPE: ClassVar[int] = 14
    __slots__ = ()


class OptBlockStateEME(EntityMetadataEntry):
    """Represents an optional block state in the world."""

    ENTRY_TYPE: ClassVar[int] = 15
    __slots__ = ()

    value: int | None

    @override
    def serialize_to(self, buf: Buffer) -> None:
        self._write_header(buf)
        if self.value is not None:
            buf.write_varint(self.value)
        else:
            buf.write_varint(0)

    @override
    @classmethod
    def read_value(cls, buf: Buffer) -> int | None:
        value = buf.read_varint()
        if value == 0:
            value = None
        return value


class NBTagEME(EntityMetadataEntry):
    """Represents an NBT entry in an entity metadata list."""

    ENTRY_TYPE: ClassVar[int] = 16
    __slots__ = ()

    value: NBTag

    @override
    def serialize_to(self, buf: Buffer) -> None:
        self._write_header(buf)
        self.value.serialize_to(buf, with_name=False)

    @override
    @classmethod
    def read_value(cls, buf: Buffer) -> NBTag:
        return NBTag.deserialize(buf, with_name=False)


class ParticleEME(EntityMetadataEntry):
    """Represents a particle entry in an entity metadata list."""

    ENTRY_TYPE: ClassVar[int] = 17
    __slots__ = ()

    value: tuple[int, Any]

    @override
    def serialize_to(self, buf: Buffer) -> None:
        self._write_header(buf)  # pragma: no cover
        buf.write_varint(self.value[0])  # pragma: no cover
        raise NotImplementedError("The rest of the particle data is not implemented yet.")  # pragma: no cover

    @override
    @classmethod
    def read_value(cls, buf: Buffer) -> tuple[int, Any]:
        value = buf.read_varint()  # pragma: no cover   # noqa: F841
        raise NotImplementedError("The rest of the particle data is not implemented yet.")


class VillagerDataEME(EntityMetadataEntry):
    """Represents a villager data entry in an entity metadata list.

    This includes the type, profession, and level of the villager.
    """

    ENTRY_TYPE: ClassVar[int] = 18
    __slots__ = ()

    value: tuple[int, int, int]

    @override
    def serialize_to(self, buf: Buffer) -> None:
        self._write_header(buf)
        buf.write_varint(self.value[0])
        buf.write_varint(self.value[1])
        buf.write_varint(self.value[2])

    @override
    @classmethod
    def read_value(cls, buf: Buffer) -> tuple[int, int, int]:
        return (buf.read_varint(), buf.read_varint(), buf.read_varint())


class OptVarIntEME(EntityMetadataEntry):
    """Represents an optional varint entry in an entity metadata list."""

    ENTRY_TYPE: ClassVar[int] = 19
    __slots__ = ()

    value: int | None

    @override
    def serialize_to(self, buf: Buffer) -> None:
        self._write_header(buf)
        # We use the old python True == 1 trick to represent a boolean
        if self.value is not None:
            buf.write_varint(self.value + 1)
        else:
            buf.write_varint(0)

    @override
    @classmethod
    def read_value(cls, buf: Buffer) -> int | None:
        value = buf.read_varint() - 1
        if value == -1:
            value = None
        return value


class PoseEME(_VarIntEnumEME):
    """Represents a pose entry in an entity metadata list."""

    ENTRY_TYPE: ClassVar[int] = 20
    __slots__ = ()
    ENUM: ClassVar[type[IntEnum]] = Pose


class CatVariantEME(_RegistryVarIntEME):
    """Represents a cat variant entry in an entity metadata list."""

    ENTRY_TYPE: ClassVar[int] = 21
    __slots__ = ()


class FrogVariantEME(_RegistryVarIntEME):
    """Represents a frog variant entry in an entity metadata list."""

    ENTRY_TYPE: ClassVar[int] = 22
    __slots__ = ()


class DragonPhaseEME(_VarIntEnumEME):
    """Represents a dragon phase entry in an entity metadata list.

    This is not a real type, because the type is VarInt, but the values are predefined.
    """

    ENTRY_TYPE: ClassVar[int] = 1
    __slots__ = ()
    ENUM: ClassVar[type[IntEnum]] = DragonPhase


class OptGlobalPositionEME(EntityMetadataEntry):
    """Represents an optional global position entry in an entity metadata list.

    This includes an identifier for the dimension as well as the position in it.
    """

    ENTRY_TYPE: ClassVar[int] = 23
    __slots__ = ()

    value: tuple[Identifier, Position] | None

    @override
    def serialize_to(self, buf: Buffer) -> None:
        self._write_header(buf)
        # We use the old python True == 1 trick to represent a boolean
        buf.write_value(StructFormat.BYTE, self.value is not None)
        if self.value is not None:
            self.value[0].serialize_to(buf)
            self.value[1].serialize_to(buf)

    @override
    @classmethod
    def read_value(cls, buf: Buffer) -> tuple[Identifier, Position] | None:
        present = buf.read_value(StructFormat.BYTE)
        if present:
            return (Identifier.deserialize(buf), Position.deserialize(buf))
        return None


class PaintingVariantEME(_RegistryVarIntEME):
    """Represents a painting variant entry in an entity metadata list."""

    ENTRY_TYPE: ClassVar[int] = 24
    __slots__ = ()


class SnifferStateEME(_VarIntEnumEME):
    """Represents a sniffer state entry in an entity metadata list."""

    ENTRY_TYPE: ClassVar[int] = 25
    __slots__ = ()
    ENUM: ClassVar[type[IntEnum]] = SnifferState


class Vector3EME(EntityMetadataEntry):
    """Represents a vector3 entry in an entity metadata list."""

    ENTRY_TYPE: ClassVar[int] = 26
    __slots__ = ()

    value: Vec3

    @override
    def serialize_to(self, buf: Buffer) -> None:
        self._write_header(buf)
        self.value.serialize_to(buf)

    @override
    @classmethod
    def read_value(cls, buf: Buffer) -> Vec3:
        return Vec3.deserialize(buf)


class QuaternionEME(EntityMetadataEntry):
    """Represents a quaternion entry in an entity metadata list."""

    ENTRY_TYPE: ClassVar[int] = 27
    __slots__ = ()

    value: Quaternion

    @override
    def serialize_to(self, buf: Buffer) -> None:
        self._write_header(buf)
        self.value.serialize_to(buf)

    @override
    @classmethod
    def read_value(cls, buf: Buffer) -> Quaternion:
        return Quaternion.deserialize(buf)


ASSOCIATIONS = {
    0: ByteEME,
    1: VarIntEME,
    2: _RegistryVarIntEME,
    3: FloatEME,
    4: StringEME,
    5: TextComponentEME,
    6: OptTextComponentEME,
    7: SlotEME,
    8: BooleanEME,
    9: RotationEME,
    10: PositionEME,
    11: OptPositionEME,
    12: DirectionEME,
    13: OptUUIDEME,
    14: BlockStateEME,
    15: OptBlockStateEME,
    16: NBTagEME,
    17: ParticleEME,
    18: VillagerDataEME,
    19: OptVarIntEME,
    20: PoseEME,
    21: CatVariantEME,
    22: FrogVariantEME,
    23: OptGlobalPositionEME,
    24: PaintingVariantEME,
    25: SnifferStateEME,
    26: Vector3EME,
    27: QuaternionEME,
}
