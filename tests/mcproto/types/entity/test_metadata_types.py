from typing import Union
from mcproto.types.entity.metadata_types import (
    PositionEME,
    OptBlockStateEME,
    Vector3EME,
    RotationEME,
    Masked,
    OptUUIDEME,
    VarIntEME,
    TextComponentEME,
    OptTextComponentEME,
    NBTagEME,
    StringEME,
    FrogVariantEME,
    PoseEME,
    BooleanEME,
    BlockStateEME,
    PaintingVariantEME,
    OptGlobalPositionEME,
    DirectionEME,
    VarLongEME,
    VillagerDataEME,
    SnifferStateEME,
    QuaternionEME,
    CatVariantEME,
    DragonPhaseEME,
    FloatEME,
    SlotEME,
    ByteEME,
    OptVarIntEME,
    OptPositionEME,
    ParticleEME,
)

from mcproto.types.slot import Slot
from mcproto.types.vec3 import Vec3, Position
from mcproto.types.quaternion import Quaternion
from mcproto.types.chat import TextComponent
from mcproto.types.nbt import NBTag, EndNBT, StringNBT, CompoundNBT, ByteNBT
from mcproto.types.uuid import UUID
from mcproto.types.identifier import Identifier
from mcproto.types.entity.enums import SnifferState, DragonPhase, Direction, Pose

from tests.helpers import gen_serializable_test

# ByteEME
gen_serializable_test(
    context=globals(),
    cls=ByteEME,
    fields=[
        ("index", int),
        ("value", int),
    ],
    serialize_deserialize=[
        ((54, 0), b"\x36\x00\x00"),
        ((1, 1), b"\x01\x00\x01"),
        ((2, 127), b"\x02\x00\x7f"),
        ((3, -1), b"\x03\x00\xff"),
        ((4, -128), b"\x04\x00\x80"),
    ],
    validation_fail=[
        ((-1, 0), ValueError),
        ((54, 128), ValueError),
        ((54, -129), ValueError),
    ],
    deserialization_fail=[
        (b"\xff\x00\x01", ValueError),  # End of metadata
        (b"\x01\x02", TypeError),  # Wrong type
    ],
)

# VarIntEME
gen_serializable_test(
    context=globals(),
    cls=VarIntEME,
    fields=[
        ("index", int),
        ("value", int),
    ],
    serialize_deserialize=[
        ((54, 0), b"\x36\x01\x00"),
        ((1, 1), b"\x01\x01\x01"),
        ((2, 127), b"\x02\x01\x7f"),
        ((3, -1), b"\x03\x01\xff\xff\xff\xff\x0f"),
        ((4, 128), b"\x04\x01\x80\x01"),
    ],
    validation_fail=[
        ((-1, 0), ValueError),
        ((54, 2**31), ValueError),
        ((54, -(2**31 + 1)), ValueError),
    ],
)

# VarLongEME
gen_serializable_test(
    context=globals(),
    cls=VarLongEME,
    fields=[
        ("index", int),
        ("value", int),
    ],
    serialize_deserialize=[
        ((54, 0), b"\x36\x02\x00"),
        ((1, 1), b"\x01\x02\x01"),
        ((2, 127), b"\x02\x02\x7f"),
        ((3, -1), b"\x03\x02\xff\xff\xff\xff\xff\xff\xff\xff\xff\x01"),
        ((4, 128), b"\x04\x02\x80\x01"),
    ],
    validation_fail=[
        ((-1, 0), ValueError),
        ((54, 2**63), ValueError),
        ((54, -(2**63 + 1)), ValueError),
    ],
)

# FloatEME
gen_serializable_test(
    context=globals(),
    cls=FloatEME,
    fields=[
        ("index", int),
        ("value", float),
    ],
    serialize_deserialize=[
        ((54, 0.0), b"\x36\x03\x00\x00\x00\x00"),
        ((1, 2.0), b"\x01\x03\x40\x00\x00\x00"),
        ((2, -1.0), b"\x02\x03\xbf\x80\x00\x00"),
        ((3, 127.0), b"\x03\x03\x42\xfe\x00\x00"),
        ((4, 0.5), b"\x04\x03\x3f\x00\x00\x00"),
    ],
    validation_fail=[
        ((-1, 0.0), ValueError),
    ],
)

# StringEME
gen_serializable_test(
    context=globals(),
    cls=StringEME,
    fields=[
        ("index", int),
        ("value", str),
    ],
    serialize_deserialize=[
        ((54, ""), b"\x36\x04\x00"),
        ((1, "a"), b"\x01\x04\x01a"),
        ((2, "abc"), b"\x02\x04\x03abc"),
    ],
    validation_fail=[
        ((-1, ""), ValueError),
        ((54, "a" * 32768), ValueError),
    ],
)

# TextComponentEME
gen_serializable_test(
    context=globals(),
    cls=TextComponentEME,
    fields=[
        ("index", int),
        ("value", TextComponent),
    ],
    serialize_deserialize=[
        ((54, TextComponent("")), b"\x36\x05" + CompoundNBT([StringNBT("", name="text")]).serialize()),
        ((1, TextComponent({"text": "a"})), b"\x01\x05" + CompoundNBT([StringNBT("a", name="text")]).serialize()),
        (
            (
                2,
                TextComponent(
                    {
                        "text": "abc",
                        "italic": False,
                        "bold": True,  # Order is not important in the result but it is in the test
                    }
                ),
            ),
            b"\x02\x05"
            + CompoundNBT([StringNBT("abc", name="text"), ByteNBT(0, "italic"), ByteNBT(1, "bold")]).serialize(),
        ),
    ],
    validation_fail=[
        ((-1, TextComponent("")), ValueError),
    ],
)

# OptTextComponentEME
gen_serializable_test(
    context=globals(),
    cls=OptTextComponentEME,
    fields=[
        ("index", int),
        ("value", Union[TextComponent, None]),
    ],
    serialize_deserialize=[
        ((54, None), b"\x36\x06\x00"),
        ((1, TextComponent("")), b"\x01\x06\x01" + CompoundNBT([StringNBT("", name="text")]).serialize()),
        ((2, TextComponent("a")), b"\x02\x06\x01" + CompoundNBT([StringNBT("a", name="text")]).serialize()),
    ],
    validation_fail=[
        ((-1, None), ValueError),
    ],
)

# SlotEME
gen_serializable_test(
    context=globals(),
    cls=SlotEME,
    fields=[
        ("index", int),
        ("value", Slot),
    ],
    serialize_deserialize=[
        (
            (54, Slot(present=True, item_id=1, item_count=1, nbt=EndNBT())),
            b"\x36\x07" + Slot(present=True, item_id=1, item_count=1).serialize(),
        ),
    ],
)

# BooleanEME
gen_serializable_test(
    context=globals(),
    cls=BooleanEME,
    fields=[
        ("index", int),
        ("value", bool),
    ],
    serialize_deserialize=[
        ((54, True), b"\x36\x08\x01"),
        ((1, False), b"\x01\x08\x00"),
    ],
    validation_fail=[
        ((-1, True), ValueError),
    ],
)

# RotationEME
gen_serializable_test(
    context=globals(),
    cls=RotationEME,
    fields=[
        ("index", int),
        ("value", Vec3),
    ],
    serialize_deserialize=[
        ((54, Vec3(0.0, 0.0, 0.0)), b"\x36\x09" + Vec3(0.0, 0.0, 0.0).serialize()),
        ((1, Vec3(1.0, 2.0, 3.0)), b"\x01\x09" + Vec3(1.0, 2.0, 3.0).serialize()),
    ],
    validation_fail=[
        ((-1, Vec3(0.0, 0.0, 0.0)), ValueError),
    ],
)

# PositionEME
gen_serializable_test(
    context=globals(),
    cls=PositionEME,
    fields=[
        ("index", int),
        ("value", Position),
    ],
    serialize_deserialize=[
        ((54, Position(0, 0, 0)), b"\x36\x0a" + Position(0, 0, 0).serialize()),
        ((1, Position(1, 2, 3)), b"\x01\x0a" + Position(1, 2, 3).serialize()),
    ],
    validation_fail=[
        ((-1, Position(0, 0, 0)), ValueError),
    ],
)

# OptPositionEME
gen_serializable_test(
    context=globals(),
    cls=OptPositionEME,
    fields=[
        ("index", int),
        ("value", Union[Position, None]),
    ],
    serialize_deserialize=[
        ((54, None), b"\x36\x0b\x00"),
        ((1, Position(0, 0, 0)), b"\x01\x0b\01" + Position(0, 0, 0).serialize()),
    ],
    validation_fail=[
        ((-1, Position(0, 0, 0)), ValueError),
    ],
)

# DirectionEME
gen_serializable_test(
    context=globals(),
    cls=DirectionEME,
    fields=[
        ("index", int),
        ("value", Direction),
    ],
    serialize_deserialize=[
        ((54, Direction.DOWN), b"\x36\x0c\x00"),
        ((1, Direction.NORTH), b"\x01\x0c\x02"),
        ((2, Direction.EAST), b"\x02\x0c\x05"),
    ],
    validation_fail=[
        ((-1, Direction.DOWN), ValueError),
    ],
    deserialization_fail=[
        (b"\x01\x0c\x0f", ValueError),
    ],
)

# OptUUIDEME
gen_serializable_test(
    context=globals(),
    cls=OptUUIDEME,
    fields=[
        ("index", int),
        ("value", Union[UUID, None]),
    ],
    serialize_deserialize=[
        ((54, None), b"\x36\r\x00"),
        ((1, UUID("0" * 32)), b"\x01\r\x01" + UUID("0" * 32).serialize()),
        ((2, UUID("f" * 32)), b"\x02\r\x01" + UUID("f" * 32).serialize()),
    ],
    validation_fail=[
        ((-1, UUID("0" * 32)), ValueError),
    ],
)

# BlockStateEME
gen_serializable_test(
    context=globals(),
    cls=BlockStateEME,
    fields=[
        ("index", int),
        ("value", int),
    ],
    serialize_deserialize=[
        ((54, 0), b"\x36\x0e\x00"),
        ((1, 1), b"\x01\x0e\x01"),
        ((2, 127), b"\x02\x0e\x7f"),
    ],
    validation_fail=[
        ((-1, 0), ValueError),
    ],
)


# OptBlockStateEME
gen_serializable_test(
    context=globals(),
    cls=OptBlockStateEME,
    fields=[
        ("index", int),
        ("value", Union[int, None]),
    ],
    serialize_deserialize=[
        ((54, None), b"\x36\x0f\x00"),
        ((1, 1), b"\x01\x0f\x01"),
        ((2, 3), b"\x02\x0f\x03"),  # Air is not representable
    ],
    validation_fail=[
        ((-1, 0), ValueError),
    ],
)

# NBTagEME
gen_serializable_test(
    context=globals(),
    cls=NBTagEME,
    fields=[
        ("index", int),
        ("value", NBTag),
    ],
    serialize_deserialize=[
        ((54, EndNBT()), b"\x36\x10" + EndNBT().serialize()),
        (
            (1, CompoundNBT([StringNBT("a", name="b")])),
            b"\x01\x10" + CompoundNBT([StringNBT("a", name="b")]).serialize(),
        ),
    ],
    validation_fail=[
        ((-1, EndNBT()), ValueError),
    ],
)

# ParticleEME
gen_serializable_test(
    context=globals(),
    cls=ParticleEME,
    fields=[
        ("index", int),
        ("value", tuple),
    ],
    deserialization_fail=[
        (b"\x01\x11\x01", NotImplementedError),
    ],
    validation_fail=[
        ((-1, (2, None)), ValueError),
    ],
)

# VillagerDataEME
gen_serializable_test(
    context=globals(),
    cls=VillagerDataEME,
    fields=[
        ("index", int),
        ("value", tuple),
    ],
    serialize_deserialize=[
        ((54, (0, 0, 0)), b"\x36\x12\x00\x00\x00"),
        ((1, (1, 2, 3)), b"\x01\x12\x01\x02\x03"),
    ],
    validation_fail=[
        ((-1, (0, 0, 0)), ValueError),
    ],
)

# OptVarIntEME
gen_serializable_test(
    context=globals(),
    cls=OptVarIntEME,
    fields=[
        ("index", int),
        ("value", Union[int, None]),
    ],
    serialize_deserialize=[
        ((54, None), b"\x36\x13\x00"),
        ((1, 0), b"\x01\x13\x01"),
        ((2, 127), b"\x02\x13\x80\x01"),
    ],
    validation_fail=[
        ((-1, 0), ValueError),
    ],
)

# PoseEME
gen_serializable_test(
    context=globals(),
    cls=PoseEME,
    fields=[
        ("index", int),
        ("value", Pose),
    ],
    serialize_deserialize=[
        ((54, Pose.STANDING), b"\x36\x14\x00"),
        ((1, Pose.SPIN_ATTACK), b"\x01\x14\x04"),
        ((2, Pose.DYING), b"\x02\x14\x07"),
    ],
    validation_fail=[
        ((-1, Pose.STANDING), ValueError),
    ],
)

# CatVariantEME
gen_serializable_test(  # Need to update when registries are implemented
    context=globals(),
    cls=CatVariantEME,
    fields=[
        ("index", int),
        ("value", int),
    ],
    serialize_deserialize=[
        ((54, 0), b"\x36\x15\x00"),
        ((1, 1), b"\x01\x15\x01"),
        ((2, 127), b"\x02\x15\x7f"),
    ],
    validation_fail=[
        ((-1, 0), ValueError),
    ],
)

# FrogVariantEME
gen_serializable_test(  # Need to update when registries are implemented
    context=globals(),
    cls=FrogVariantEME,
    fields=[
        ("index", int),
        ("value", int),
    ],
    serialize_deserialize=[
        ((54, 0), b"\x36\x16\x00"),
        ((1, 1), b"\x01\x16\x01"),
        ((2, 127), b"\x02\x16\x7f"),
    ],
    validation_fail=[
        ((-1, 0), ValueError),
    ],
)

# DragonPhaseEME
gen_serializable_test(
    context=globals(),
    cls=DragonPhaseEME,
    fields=[
        ("index", int),
        ("value", DragonPhase),
    ],
    serialize_deserialize=[  # 0x01 because it is really a varint and not an Enum, I wanted better readability
        ((54, DragonPhase.CIRCLING), b"\x36\x01\x00"),
        ((1, DragonPhase.STRAFING), b"\x01\x01\x01"),
        ((2, DragonPhase.LANDED_BREATH_ATTACK), b"\x02\x01\x05"),
    ],
    validation_fail=[
        ((-1, DragonPhase.CIRCLING), ValueError),
    ],
)

# OptGlobalPositionEME
gen_serializable_test(
    context=globals(),
    cls=OptGlobalPositionEME,
    fields=[
        ("index", int),
        ("value", tuple),  # Identifier, Position | None
    ],
    serialize_deserialize=[
        ((54, None), b"\x36\x17\x00"),
        (
            (1, (Identifier("minecraft", "overworld"), Position(4, 5, 6))),
            b"\x01\x17\x01" + Identifier("minecraft", "overworld").serialize() + Position(4, 5, 6).serialize(),
        ),
    ],
)

# PaintingVariantEME
gen_serializable_test(  # Need to update when registries are implemented
    context=globals(),
    cls=PaintingVariantEME,
    fields=[
        ("index", int),
        ("value", int),
    ],
    serialize_deserialize=[
        ((54, 0), b"\x36\x18\x00"),
        ((1, 1), b"\x01\x18\x01"),
        ((2, 127), b"\x02\x18\x7f"),
    ],
    validation_fail=[
        ((-1, 0), ValueError),
    ],
)


# SnifferStateEME
gen_serializable_test(
    context=globals(),
    cls=SnifferStateEME,
    fields=[
        ("index", int),
        ("value", SnifferState),
    ],
    serialize_deserialize=[
        ((54, SnifferState.IDLING), b"\x36\x19\x00"),
        ((1, SnifferState.SNIFFING), b"\x01\x19\x03"),
        ((2, SnifferState.RISING), b"\x02\x19\x06"),
    ],
    validation_fail=[
        ((-1, SnifferState.IDLING), ValueError),
        ((1, 0xF), ValueError),
    ],
    deserialization_fail=[
        (b"\x01\x19\x0f", ValueError),
    ],
)

# Vector3EME
gen_serializable_test(
    context=globals(),
    cls=Vector3EME,
    fields=[
        ("index", int),
        ("value", Vec3),
    ],
    serialize_deserialize=[
        ((54, Vec3(0.0, 0.0, 0.0)), b"\x36\x1a" + Vec3(0.0, 0.0, 0.0).serialize()),
        ((1, Vec3(1.0, 2.0, 3.0)), b"\x01\x1a" + Vec3(1.0, 2.0, 3.0).serialize()),
    ],
    validation_fail=[
        ((-1, Vec3(0.0, 0.0, 0.0)), ValueError),
    ],
)

# QuaternionEME
gen_serializable_test(
    context=globals(),
    cls=QuaternionEME,
    fields=[
        ("index", int),
        ("value", Quaternion),
    ],
    serialize_deserialize=[
        ((54, Quaternion(0.0, 0.0, 0.0, 1.0)), b"\x36\x1b" + Quaternion(0.0, 0.0, 0.0, 1.0).serialize()),
        ((1, Quaternion(1.0, 2.0, 3.0, 4.0)), b"\x01\x1b" + Quaternion(1.0, 2.0, 3.0, 4.0).serialize()),
    ],
    validation_fail=[
        ((-1, Quaternion(0.0, 0.0, 0.0, 1.0)), ValueError),
    ],
)


def test_masked():
    """Test the Masked class."""
    container = ByteEME(index=1, value=0)
    mask1 = Masked(container, mask=0b00000001)
    mask2 = Masked(container, mask=0b00000010)
    mask3 = Masked(container, mask=0b00000100)
    mask12 = Masked(container, mask=0b00000011)
    mask13 = Masked(container, mask=0b00000101)

    assert mask1.getter() == 0
    assert mask2.getter() == 0
    assert mask3.getter() == 0
    assert mask12.getter() == 0
    assert mask13.getter() == 0

    mask1.setter(1)
    mask2.setter(1)
    assert mask1.getter() == 1
    assert mask2.getter() == 1
    assert mask3.getter() == 0
    assert mask12.getter() == 3
    assert mask13.getter() == 1

    mask1.setter(0)
    mask3.setter(1)
    assert mask1.getter() == 0
    assert mask13.getter() == 2

    mask12.setter(0)
    assert mask12.getter() == 0
    assert mask13.getter() == 2
    assert mask1.getter() == 0
    assert mask2.getter() == 0
    assert mask3.getter() == 1
