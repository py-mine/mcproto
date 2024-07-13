from __future__ import annotations

import struct
from typing import Any, cast

import pytest

from mcproto.buffer import Buffer
from mcproto.types.nbt import (
    ByteArrayNBT,
    ByteNBT,
    CompoundNBT,
    DoubleNBT,
    EndNBT,
    FloatNBT,
    FromObjectSchema,
    FromObjectType,
    IntArrayNBT,
    IntNBT,
    ListNBT,
    LongArrayNBT,
    LongNBT,
    NBTag,
    ShortNBT,
    StringNBT,
)
from tests.helpers import gen_serializable_test

# region EndNBT

gen_serializable_test(
    context=globals(),
    cls=EndNBT,
    fields=[],
    serialize_deserialize=[
        ((), b"\x00"),
    ],
    deserialization_fail=[
        (b"\x01", IOError),
    ],
)


# endregion
# region Numerical NBT tests

gen_serializable_test(
    context=globals(),
    cls=ByteNBT,
    fields=[("payload", int), ("name", str)],
    serialize_deserialize=[
        ((0, "a"), b"\x01\x00\x01a\x00"),
        ((1, "test"), b"\x01\x00\x04test\x01"),
        ((127, "&à@é"), b"\x01\x00\x06" + bytes("&à@é", "utf-8") + b"\x7f"),
        ((-128, "test"), b"\x01\x00\x04test\x80"),
        ((-1, "a" * 100), b"\x01\x00\x64" + b"a" * 100 + b"\xff"),
    ],
    deserialization_fail=[
        # Errors
        (b"\x01\x00\x04test", IOError),
        (b"\x01\x00\x04tes", IOError),
        (b"\x01\x00", IOError),
        (b"\x01", IOError),
        # Wrong type
        (b"\x02\x00\x01a\x00", TypeError),
        (b"\xff\x00\x01a\x00", TypeError),
    ],
    validation_fail=[
        # Out of bounds
        ((1 << 7, "a"), OverflowError),
        ((-(1 << 7) - 1, "a"), OverflowError),
        ((1 << 8, "a"), OverflowError),
        ((-(1 << 8) - 1, "a"), OverflowError),
        ((1000, "a"), OverflowError),
        ((1.5, "a"), TypeError),
    ],
)

gen_serializable_test(
    context=globals(),
    cls=ShortNBT,
    fields=[("payload", int), ("name", str)],
    serialize_deserialize=[
        ((0, "a"), b"\x02\x00\x01a\x00\x00"),
        ((1, "test"), b"\x02\x00\x04test\x00\x01"),
        ((32767, "&à@é"), b"\x02\x00\x06" + bytes("&à@é", "utf-8") + b"\x7f\xff"),
        ((-32768, "test"), b"\x02\x00\x04test\x80\x00"),
        ((-1, "a" * 100), b"\x02\x00\x64" + b"a" * 100 + b"\xff\xff"),
    ],
    deserialization_fail=[
        # Errors
        (b"\x02\x00\x04test", IOError),
        (b"\x02\x00\x04tes", IOError),
        (b"\x02\x00", IOError),
        (b"\x02", IOError),
    ],
    validation_fail=[
        # Out of bounds
        ((1 << 15, "a"), OverflowError),
        ((-(1 << 15) - 1, "a"), OverflowError),
        ((1 << 16, "a"), OverflowError),
        ((-(1 << 16) - 1, "a"), OverflowError),
        ((int(1e10), "a"), OverflowError),
    ],
)

gen_serializable_test(
    context=globals(),
    cls=IntNBT,
    fields=[("payload", int), ("name", str)],
    serialize_deserialize=[
        ((0, "a"), b"\x03\x00\x01a\x00\x00\x00\x00"),
        ((1, "test"), b"\x03\x00\x04test\x00\x00\x00\x01"),
        ((2147483647, "&à@é"), b"\x03\x00\x06" + bytes("&à@é", "utf-8") + b"\x7f\xff\xff\xff"),
        ((-2147483648, "test"), b"\x03\x00\x04test\x80\x00\x00\x00"),
        ((-1, "a" * 100), b"\x03\x00\x64" + b"a" * 100 + b"\xff\xff\xff\xff"),
    ],
    deserialization_fail=[
        # Errors
        (b"\x03\x00\x04test", IOError),
        (b"\x03\x00\x04tes", IOError),
        (b"\x03\x00", IOError),
        (b"\x03", IOError),
    ],
    validation_fail=[
        # Out of bounds
        ((1 << 31, "a"), OverflowError),
        ((-(1 << 31) - 1, "a"), OverflowError),
        ((1 << 32, "a"), OverflowError),
        ((-(1 << 32) - 1, "a"), OverflowError),
        ((int(1e30), "a"), OverflowError),
    ],
)

gen_serializable_test(
    context=globals(),
    cls=LongNBT,
    fields=[("payload", int), ("name", str)],
    serialize_deserialize=[
        ((0, "a"), b"\x04\x00\x01a\x00\x00\x00\x00\x00\x00\x00\x00"),
        ((1, "test"), b"\x04\x00\x04test\x00\x00\x00\x00\x00\x00\x00\x01"),
        (((1 << 63) - 1, "&à@é"), b"\x04\x00\x06" + bytes("&à@é", "utf-8") + b"\x7f\xff\xff\xff\xff\xff\xff\xff"),
        ((-1 << 63, "test"), b"\x04\x00\x04test\x80\x00\x00\x00\x00\x00\x00\x00"),
        ((-1, "a" * 100), b"\x04\x00\x64" + b"a" * 100 + b"\xff\xff\xff\xff\xff\xff\xff\xff"),
    ],
    deserialization_fail=[
        # Errors
        (b"\x04\x00\x04test", IOError),
        (b"\x04\x00\x04tes", IOError),
        (b"\x04\x00", IOError),
        (b"\x04", IOError),
    ],
    validation_fail=[
        # Out of bounds
        ((1 << 63, "a"), OverflowError),
        ((-(1 << 63) - 1, "a"), OverflowError),
        ((1 << 64, "a"), OverflowError),
        ((-(1 << 64) - 1, "a"), OverflowError),
    ],
)


# endregion
# region Floating point NBT tests
gen_serializable_test(
    context=globals(),
    cls=FloatNBT,
    fields=[("payload", float), ("name", str)],
    serialize_deserialize=[
        ((1.0, "a"), b"\x05\x00\x01a" + bytes(struct.pack(">f", 1.0))),
        ((0.5, "test"), b"\x05\x00\x04test" + bytes(struct.pack(">f", 0.5))),  # has to be convertible to float exactly
        ((-1.0, "&à@é"), b"\x05\x00\x06" + bytes("&à@é", "utf-8") + bytes(struct.pack(">f", -1.0))),
        ((12.0, "a" * 100), b"\x05\x00\x64" + b"a" * 100 + bytes(struct.pack(">f", 12.0))),
        ((1, "a"), b"\x05\x00\x01a" + bytes(struct.pack(">f", 1.0))),
    ],
    deserialization_fail=[
        # Errors
        (b"\x05\x00\x04test", IOError),
        (b"\x05\x00\x04tes", IOError),
        (b"\x05\x00", IOError),
        (b"\x05", IOError),
    ],
    validation_fail=[
        # Wrong type
        (("1.5", "a"), TypeError),
    ],
)

gen_serializable_test(
    context=globals(),
    cls=DoubleNBT,
    fields=[("payload", float), ("name", str)],
    serialize_deserialize=[
        ((1.0, "a"), b"\x06\x00\x01a" + bytes(struct.pack(">d", 1.0))),
        ((3.14, "test"), b"\x06\x00\x04test" + bytes(struct.pack(">d", 3.14))),
        ((-1.0, "&à@é"), b"\x06\x00\x06" + bytes("&à@é", "utf-8") + bytes(struct.pack(">d", -1.0))),
        ((12.0, "a" * 100), b"\x06\x00\x64" + b"a" * 100 + bytes(struct.pack(">d", 12.0))),
    ],
    deserialization_fail=[
        # Errors
        (b"\x06\x00\x04test\x01", IOError),
        (b"\x06\x00\x04test", IOError),
        (b"\x06\x00\x04tes", IOError),
        (b"\x06\x00", IOError),
        (b"\x06", IOError),
    ],
)

# endregion
# region Variable Length NBT tests
gen_serializable_test(
    context=globals(),
    cls=ByteArrayNBT,
    fields=[("payload", bytes), ("name", str)],
    serialize_deserialize=[
        ((b"", "a"), b"\x07\x00\x01a\x00\x00\x00\x00"),
        ((b"\x00", "test"), b"\x07\x00\x04test\x00\x00\x00\x01\x00"),
        ((b"\x00\x01", "&à@é"), b"\x07\x00\x06" + bytes("&à@é", "utf-8") + b"\x00\x00\x00\x02\x00\x01"),
        ((b"\x00\x01\x02", "test"), b"\x07\x00\x04test\x00\x00\x00\x03\x00\x01\x02"),
        ((b"\xff" * 1024, "a" * 100), b"\x07\x00\x64" + b"a" * 100 + b"\x00\x00\x04\x00" + b"\xff" * 1024),
        ((b"Hello World", "test"), b"\x07\x00\x04test\x00\x00\x00\x0b" + b"Hello World"),
        ((bytearray(b"Hello World"), "test"), b"\x07\x00\x04test\x00\x00\x00\x0b" + b"Hello World"),
    ],
    deserialization_fail=[
        # Errors
        (b"\x07\x00\x04test", IOError),
        (b"\x07\x00\x04tes", IOError),
        (b"\x07\x00", IOError),
        (b"\x07", IOError),
        (b"\x07\x00\x01a\x00\x01", IOError),
        (b"\x07\x00\x01a\x00\x00\x00\xff", IOError),
        # Negative length
        (b"\x07\x00\x01a\xff\xff\xff\xff", ValueError),
    ],
    validation_fail=[
        # Wrong type
        ((1, "a"), TypeError),
    ],
)

gen_serializable_test(
    context=globals(),
    cls=StringNBT,
    fields=[("payload", str), ("name", str)],
    serialize_deserialize=[
        (("", "a"), b"\x08\x00\x01a\x00\x00"),
        (("test", "a"), b"\x08\x00\x01a\x00\x04" + b"test"),
        (("a" * 100, "&à@é"), b"\x08\x00\x06" + bytes("&à@é", "utf-8") + b"\x00\x64" + b"a" * 100),
        (("&à@é", "test"), b"\x08\x00\x04test\x00\x06" + bytes("&à@é", "utf-8")),
    ],
    deserialization_fail=[
        # Errors
        (b"\x08\x00\x04test", IOError),
        (b"\x08\x00\x04tes", IOError),
        (b"\x08\x00", IOError),
        (b"\x08", IOError),
        # Unicode decode error
        (b"\x08\x00\x01a\x00\x01\xff", UnicodeDecodeError),
        (b"\x08\xff\xff\xff\xff", ValueError),
    ],
    validation_fail=[
        # Negative length
        # String too long
        (("a" * 32768, "b"), ValueError),
        # Wrong type
        ((1, "a"), TypeError),
        # Unpaired surrogate
        (("\udc80", "a"), ValueError),
    ],
)

gen_serializable_test(
    context=globals(),
    cls=ListNBT,
    fields=[("payload", list), ("name", str)],
    serialize_deserialize=[
        (([], "a"), b"\x09\x00\x01a\x00\x00\x00\x00\x00"),
        (([ByteNBT(-1)], "a"), b"\x09\x00\x01a\x01\x00\x00\x00\x01\xff"),
        (([ListNBT([])], "a"), b"\x09\x00\x01a\x09\x00\x00\x00\x01" + ListNBT([]).serialize()[1:]),
        (([ListNBT([ByteNBT(6)])], "a"), b"\x09\x00\x01a\x09\x00\x00\x00\x01" + ListNBT([ByteNBT(6)]).serialize()[1:]),
        (
            ([ListNBT([ByteNBT(-1)]), ListNBT([IntNBT(1234)])], "a"),
            b"\x09\x00\x01a\x09\x00\x00\x00\x02"
            + ListNBT([ByteNBT(-1)]).serialize()[1:]
            + ListNBT([IntNBT(1234)]).serialize()[1:],
        ),
        (
            ([ListNBT([ByteNBT(-1)]), ListNBT([IntNBT(128), IntNBT(8)])], "a"),
            b"\x09\x00\x01a\x09\x00\x00\x00\x02"
            + ListNBT([ByteNBT(-1)]).serialize()[1:]
            + ListNBT([IntNBT(128), IntNBT(8)]).serialize()[1:],
        ),
    ],
    deserialization_fail=[
        # Not enough data
        (b"\x09\x00\x01a", IOError),
        (b"\x09\x00\x01a\x01", IOError),
        (b"\x09\x00\x01a\x01\x00", IOError),
        (b"\x09\x00\x01a\x01\x00\x00\x00\x01", IOError),
        (b"\x09\x00\x01a\x01\x00\x00\x00\x03\x01", IOError),
        # Invalid tag type
        (b"\x09\x00\x01a\xff\x00\x00\x01\x00", TypeError),
    ],
    validation_fail=[
        # Not NBTags
        (([1, 2, 3], "a"), TypeError),
        # Not the same tag type
        (([ByteNBT(0), IntNBT(0)], "a"), TypeError),
        # Contains named tags
        (([ByteNBT(0, name="Byte")], "a"), ValueError),
        # Wrong type
        ((1, "a"), TypeError),
    ],
)

gen_serializable_test(
    context=globals(),
    cls=CompoundNBT,
    fields=[("payload", list), ("name", str)],
    serialize_deserialize=[
        (([], "a"), b"\x0a\x00\x01a\x00"),
        (([ByteNBT(0, name="Byte")], "a"), b"\x0a\x00\x01a" + ByteNBT(0, name="Byte").serialize() + b"\x00"),
        (
            ([ShortNBT(128, "Short"), ByteNBT(-1, "Byte")], "a"),
            b"\x0a\x00\x01a" + ShortNBT(128, "Short").serialize() + ByteNBT(-1, "Byte").serialize() + b"\x00",
        ),
        (
            ([CompoundNBT([ByteNBT(0, name="Byte")], name="test")], "a"),
            b"\x0a\x00\x01a" + CompoundNBT([ByteNBT(0, name="Byte")], "test").serialize() + b"\x00",
        ),
        (
            ([ListNBT([ByteNBT(0)] * 3, name="List")], "a"),
            b"\x0a\x00\x01a" + ListNBT([ByteNBT(0)] * 3, name="List").serialize() + b"\x00",
        ),
    ],
    deserialization_fail=[
        # Not enough data
        (b"\x0a\x00\x01a", IOError),
        (b"\x0a\x00\x01a\x01", IOError),
    ],
    validation_fail=[
        # All must be NBTags
        (([0, 1, 2], "a"), TypeError),
        # All with a name
        (([ByteNBT(0)], "a"), ValueError),
        # Names must be unique
        (([ByteNBT(0, name="Byte"), ByteNBT(0, name="Byte")], "a"), ValueError),
        # Wrong type
        ((1, "a"), TypeError),
    ],
)

gen_serializable_test(
    context=globals(),
    cls=IntArrayNBT,
    fields=[("payload", list), ("name", str)],
    serialize_deserialize=[
        (([], "a"), b"\x0b\x00\x01a\x00\x00\x00\x00"),
        (([0], "a"), b"\x0b\x00\x01a\x00\x00\x00\x01\x00\x00\x00\x00"),
        (([0, 1], "a"), b"\x0b\x00\x01a\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x01"),
        (([1, 2, 3], "a"), b"\x0b\x00\x01a\x00\x00\x00\x03\x00\x00\x00\x01\x00\x00\x00\x02\x00\x00\x00\x03"),
        (([(1 << 31) - 1], "a"), b"\x0b\x00\x01a\x00\x00\x00\x01\x7f\xff\xff\xff"),
        (([-1, -2, -3], "a"), b"\x0b\x00\x01a\x00\x00\x00\x03\xff\xff\xff\xff\xff\xff\xff\xfe\xff\xff\xff\xfd"),
    ],
    deserialization_fail=[
        # Not enough data
        (b"\x0b\x00\x01a", IOError),
        (b"\x0b\x00\x01a\x01", IOError),
        (b"\x0b\x00\x01a\x00\x00\x00\x01", IOError),
        (b"\x0b\x00\x01a\x00\x00\x00\x03\x01", IOError),
    ],
    validation_fail=[
        # Must contain ints only
        ((["a"], "a"), TypeError),
        (([IntNBT(0)], "a"), TypeError),
        (([1 << 31], "a"), OverflowError),
        (([-(1 << 31) - 1], "a"), OverflowError),
        # Wrong type
        ((1, "a"), TypeError),
    ],
)

gen_serializable_test(
    context=globals(),
    cls=LongArrayNBT,
    fields=[("payload", list), ("name", str)],
    serialize_deserialize=[
        (([], "a"), b"\x0c\x00\x01a\x00\x00\x00\x00"),
        (([0], "a"), b"\x0c\x00\x01a\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00"),
        (
            ([0, 1], "a"),
            b"\x0c\x00\x01a\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01",
        ),
        (([(1 << 63) - 1], "a"), b"\x0c\x00\x01a\x00\x00\x00\x01\x7f\xff\xff\xff\xff\xff\xff\xff"),
        (
            ([-1, -2], "a"),
            b"\x0c\x00\x01a\x00\x00\x00\x02\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xfe",
        ),
    ],
    deserialization_fail=[
        # Not enough data
        (b"\x0c\x00\x01a", IOError),
        (b"\x0c\x00\x01a\x01", IOError),
        (b"\x0c\x00\x01a\x00\x00\x00\x01", IOError),
        (b"\x0c\x00\x01a\x00\x00\x00\x03\x01", IOError),
    ],
    validation_fail=[
        # Must contain longs only
        ((["a"], "a"), TypeError),
        (([LongNBT(0)], "a"), TypeError),
        (([1 << 63], "a"), OverflowError),
        (([-(1 << 63) - 1], "a"), OverflowError),
    ],
)

# endregion


# region CompoundNBT
def test_equality_compound():
    """Test equality of CompoundNBT."""
    comp1 = CompoundNBT([ByteNBT(0, name="test"), ByteNBT(1, name="test2"), ByteNBT(2, name="test3")], "comp")
    comp2 = CompoundNBT([ByteNBT(0, name="test"), ByteNBT(1, name="test2"), ByteNBT(2, name="test3")], "comp")
    assert comp1 == comp2

    comp2 = CompoundNBT([ByteNBT(0, name="test"), ByteNBT(1, name="test2")], "comp")
    assert comp1 != comp2

    comp2 = CompoundNBT([ByteNBT(0, name="test"), ByteNBT(1, name="test2"), ByteNBT(2, name="test4")], "comp")
    assert comp1 != comp2

    comp2 = CompoundNBT([ByteNBT(0, name="test"), ByteNBT(1, name="test2"), ByteNBT(2, name="test3")], "comp2")
    assert comp1 != comp2

    assert comp1 != ByteNBT(0, name="comp")


# endregion

# region ListNBT


def test_intarray_negative_length():
    """Test IntArray with negative length."""
    buffer = Buffer(b"\x0b\x00\x01a\xff\xff\xff\xff")
    assert IntArrayNBT.read_from(buffer) == IntArrayNBT([], "a")


# endregion

# region NBTag


def test_nbt_helloworld():
    """Test serialization/deserialization of a simple NBT tag.

    Source data: https://minecraft.wiki/w/Minecraft_Wiki:Projects/wiki.vg_merge/NBT#test.nbt
    """
    data = bytearray.fromhex("0a000b68656c6c6f20776f726c640800046e616d65000942616e616e72616d6100")
    buffer = Buffer(data)

    expected_object = {
        "name": "Bananrama",
    }
    expected_schema = {"name": StringNBT}

    data = CompoundNBT.deserialize(buffer)
    assert data == NBTag.from_object(expected_object, schema=expected_schema, name="hello world")
    assert data.to_object() == expected_object


def test_nbt_bigfile():
    """Test serialization/deserialization of a big NBT tag.

    Slighly modified from the source data to also include a IntArrayNBT and a LongArrayNBT.
    Source data: https://minecraft.wiki/w/Minecraft_Wiki:Projects/wiki.vg_merge/NBT#bigtest.nbt
    """
    data = "0a00054c6576656c0400086c6f6e67546573747fffffffffffffff02000973686f7274546573747fff08000a737472696e6754657374002948454c4c4f20574f524c4420544849532049532041205445535420535452494e4720c385c384c39621050009666c6f6174546573743eff1832030007696e74546573747fffffff0a00146e657374656420636f6d706f756e6420746573740a000368616d0800046e616d65000648616d70757305000576616c75653f400000000a00036567670800046e616d6500074567676265727405000576616c75653f00000000000c000f6c6973745465737420286c6f6e672900000005000000000000000b000000000000000c000000000000000d000000000000000e7fffffffffffffff0b000e6c697374546573742028696e7429000000047fffffff7ffffffe7ffffffd7ffffffc0900136c697374546573742028636f6d706f756e64290a000000020800046e616d65000f436f6d706f756e642074616720233004000a637265617465642d6f6e000001265237d58d000800046e616d65000f436f6d706f756e642074616720233104000a637265617465642d6f6e000001265237d58d0001000862797465546573747f07006562797465417272617954657374202874686520666972737420313030302076616c756573206f6620286e2a6e2a3235352b6e2a3729253130302c207374617274696e672077697468206e3d302028302c2036322c2033342c2031362c20382c202e2e2e2929000003e8003e2210080a162c4c12462004564e505c0e2e5828024a3830323e54103a0a482c1a12142036561c502a0e60585a02183862320c54423a3c485e1a44145236241c1e2a4060265a34180662000c2242083c165e4c44465204244e1e5c402e2628344a0630003e2210080a162c4c12462004564e505c0e2e5828024a3830323e54103a0a482c1a12142036561c502a0e60585a02183862320c54423a3c485e1a44145236241c1e2a4060265a34180662000c2242083c165e4c44465204244e1e5c402e2628344a0630003e2210080a162c4c12462004564e505c0e2e5828024a3830323e54103a0a482c1a12142036561c502a0e60585a02183862320c54423a3c485e1a44145236241c1e2a4060265a34180662000c2242083c165e4c44465204244e1e5c402e2628344a0630003e2210080a162c4c12462004564e505c0e2e5828024a3830323e54103a0a482c1a12142036561c502a0e60585a02183862320c54423a3c485e1a44145236241c1e2a4060265a34180662000c2242083c165e4c44465204244e1e5c402e2628344a0630003e2210080a162c4c12462004564e505c0e2e5828024a3830323e54103a0a482c1a12142036561c502a0e60585a02183862320c54423a3c485e1a44145236241c1e2a4060265a34180662000c2242083c165e4c44465204244e1e5c402e2628344a0630003e2210080a162c4c12462004564e505c0e2e5828024a3830323e54103a0a482c1a12142036561c502a0e60585a02183862320c54423a3c485e1a44145236241c1e2a4060265a34180662000c2242083c165e4c44465204244e1e5c402e2628344a0630003e2210080a162c4c12462004564e505c0e2e5828024a3830323e54103a0a482c1a12142036561c502a0e60585a02183862320c54423a3c485e1a44145236241c1e2a4060265a34180662000c2242083c165e4c44465204244e1e5c402e2628344a0630003e2210080a162c4c12462004564e505c0e2e5828024a3830323e54103a0a482c1a12142036561c502a0e60585a02183862320c54423a3c485e1a44145236241c1e2a4060265a34180662000c2242083c165e4c44465204244e1e5c402e2628344a0630003e2210080a162c4c12462004564e505c0e2e5828024a3830323e54103a0a482c1a12142036561c502a0e60585a02183862320c54423a3c485e1a44145236241c1e2a4060265a34180662000c2242083c165e4c44465204244e1e5c402e2628344a0630003e2210080a162c4c12462004564e505c0e2e5828024a3830323e54103a0a482c1a12142036561c502a0e60585a02183862320c54423a3c485e1a44145236241c1e2a4060265a34180662000c2242083c165e4c44465204244e1e5c402e2628344a063005000a646f75626c65546573743efc000000"  # noqa: E501
    data = bytes.fromhex(data)
    buffer = Buffer(data)

    expected_object: FromObjectType = {  # Name ! Level
        "longTest": 9223372036854775807,
        "shortTest": 32767,
        "stringTest": "HELLO WORLD THIS IS A TEST STRING ÅÄÖ!",
        "floatTest": 0.4982314705848694,
        "intTest": 2147483647,
        "nested compound test": {
            "ham": {"name": "Hampus", "value": 0.75},
            "egg": {"name": "Eggbert", "value": 0.5},
        },
        "listTest (long)": [11, 12, 13, 14, 9223372036854775807],
        "listTest (int)": [2147483647, 2147483646, 2147483645, 2147483644],
        "listTest (compound)": [
            {"name": "Compound tag #0", "created-on": 1264099775885},
            {"name": "Compound tag #1", "created-on": 1264099775885},
        ],
        "byteTest": 127,
        "byteArrayTest (the first 1000 values of (n*n*255+n*7)%100, starting with n=0 (0, 62, 34, 16, 8, ...))": bytes(
            (n * n * 255 + n * 7) % 100 for n in range(1000)
        ),
        "doubleTest": 0.4921875,
    }
    expected_schema: FromObjectSchema = {
        "longTest": LongNBT,
        "shortTest": ShortNBT,
        "stringTest": StringNBT,
        "floatTest": FloatNBT,
        "intTest": IntNBT,
        "nested compound test": {
            "ham": {
                "name": StringNBT,
                "value": FloatNBT,
            },
            "egg": {
                "name": StringNBT,
                "value": FloatNBT,
            },
        },
        "listTest (long)": LongArrayNBT,
        "listTest (int)": IntArrayNBT,
        "listTest (compound)": [
            {
                "name": StringNBT,
                "created-on": LongNBT,
            }
        ],
        "byteTest": ByteNBT,
        "byteArrayTest (the first 1000 values of (n*n*255+n*7)%100, "
        "starting with n=0 (0, 62, 34, 16, 8, ...))": ByteArrayNBT,
        "doubleTest": FloatNBT,
    }

    data = CompoundNBT.deserialize(buffer)

    def check_equality(self: object, other: object) -> bool:
        """Check if two objects are equal, with deep epsilon check for floats."""
        if type(self) is not type(other):
            return False
        if isinstance(self, dict):
            self = cast("dict[Any, Any]", self)
            other = cast("dict[Any, Any]", other)
            if len(self) != len(other):
                return False
            for key in self:
                if key not in other:
                    return False
                if not check_equality(self[key], other[key]):
                    return False
            return True
        if isinstance(self, list):
            self = cast("list[Any]", self)
            other = cast("list[Any]", other)
            if len(self) != len(other):
                return False
            return all(check_equality(self[i], other[i]) for i in range(len(self)))
        if isinstance(self, float) and isinstance(other, float):
            return abs(self - other) < 1e-6
        if self != other:
            return False
        return self == other

    assert data == NBTag.from_object(expected_object, schema=expected_schema, name="Level")
    assert check_equality(data.to_object(), expected_object)


# endregion
# region Edge cases
def test_from_object_morecases():
    """Test from_object with more edge cases."""

    class CustomType:
        def to_nbt(self, name: str = "") -> NBTag:
            return ByteArrayNBT(b"CustomType", name)

    assert NBTag.from_object(
        {
            "number": ByteNBT(0),  # ByteNBT
            "bytearray": b"test",  # Conversion from bytes
            "empty_list": [],  # Empty list with type EndNBT
            "empty_compound": {},  # Empty compound
            "custom": CustomType(),  # Custom type with to_nbt method
            "recursive_list": [
                [0, 1, 2],
                [3, 4, 5],
            ],
        },
        {
            "number": ByteNBT,
            "bytearray": ByteArrayNBT,
            "empty_list": [],
            "empty_compound": {},
            "custom": CustomType,
            "recursive_list": [[IntNBT], [ShortNBT]],
        },
    ) == CompoundNBT(
        [  # Order is shuffled because the spec does not require a specific order
            CompoundNBT([], "empty_compound"),
            ByteArrayNBT(b"test", "bytearray"),
            ByteArrayNBT(b"CustomType", "custom"),
            ListNBT([], "empty_list"),
            ByteNBT(0, "number"),
            ListNBT(
                [ListNBT([IntNBT(0), IntNBT(1), IntNBT(2)]), ListNBT([ShortNBT(3), ShortNBT(4), ShortNBT(5)])],
                "recursive_list",
            ),
        ]
    )

    compound = CompoundNBT.from_object(
        {"test": 0, "test2": 0},
        {"test": ByteNBT, "test2": IntNBT},
        name="compound",
    )

    assert ListNBT([]).value == []
    assert compound.to_object(include_name=True) == {"compound": {"test": 0, "test2": 0}}
    assert compound.value == {"test": 0, "test2": 0}
    assert ListNBT([IntNBT(0)]).value == [0]

    assert ByteNBT(12).value == 12
    assert ShortNBT(13).value == 13
    assert IntNBT(14).value == 14
    assert LongNBT(15).value == 15
    assert FloatNBT(0.5).value == 0.5
    assert DoubleNBT(0.6).value == 0.6
    assert ByteArrayNBT(b"test").value == b"test"
    assert StringNBT("test").value == "test"
    assert IntArrayNBT([0, 1, 2]).value == [0, 1, 2]
    assert LongArrayNBT([0, 1, 2, 3]).value == [0, 1, 2, 3]


@pytest.mark.parametrize(
    ("data", "schema", "error", "error_msg"),
    [
        # Data is not a list
        ({"test": 0}, {"test": [ByteNBT]}, TypeError, "Expected a list, but found int."),
        # Expected a list of dict, got a list of NBTags for schema
        (
            {"test": [1, 0]},
            {"test": [ByteNBT, IntNBT]},
            TypeError,
            "The schema must contain a single type of elements. .*",
        ),
        # Schema and data have different lengths
        (
            [[1], [2], [3]],
            [[ByteNBT], [IntNBT]],
            ValueError,
            "The schema and the data must have the same length.",
        ),
        ([1], [], ValueError, "The schema and the data must have the same length."),
        # Schema is a dict, data is not
        (["test"], {"test": ByteNBT}, TypeError, "Expected a dictionary, but found a different type."),
        # Schema is not a dict, list or subclass of NBTagConvertible
        (
            ["test"],
            "test",
            TypeError,
            "The schema must be a list, dict, a subclass of NBTag or an object with a `to_nbt` method.",
        ),
        # Schema contains a mix of dict and list
        (
            [{"test": 0}, [1, 2, 3]],
            [{"test": ByteNBT}, [IntNBT]],
            TypeError,
            "Expected a list of lists or dictionaries, but found a different type",
        ),
        # Schema contains multiple types
        (
            [[0], [-1]],
            [IntArrayNBT, LongArrayNBT],
            TypeError,
            "The schema must contain a single type of elements.",
        ),
        # Schema contains CompoundNBT or ListNBT instead of a dict or list
        (
            {"test": 0},
            CompoundNBT,
            ValueError,
            "Use a list or a dictionary in the schema to create a CompoundNBT or a ListNBT.",
        ),
        (
            ["test"],
            ListNBT,
            ValueError,
            "Use a list or a dictionary in the schema to create a CompoundNBT or a ListNBT.",
        ),
        # The schema specifies a type, but the data is a dict with more than one key
        (
            {"test": 0, "test2": 1},
            ByteNBT,
            ValueError,
            "Expected a dictionary with a single key-value pair.",
        ),
        # The data is not of the right type to be a payload
        (
            {"test": object()},
            ByteNBT,
            TypeError,
            r"Expected one of \(bytes, str, int, float, list\), but found object.",
        ),
        # The data is a list but not all elements are ints
        (
            [0, "test"],
            IntArrayNBT,
            TypeError,
            "Expected a list of integers.",
        ),
    ],
)
def test_from_object_error(data: Any, schema: Any, error: type[Exception], error_msg: str):
    """Test from_object with erroneous data."""
    with pytest.raises(error, match=error_msg):
        _ = NBTag.from_object(data, schema)


def test_from_object_more_errors():
    """Test from_object with more edge cases."""
    # Redefine the name of the tag
    schema = ByteNBT
    data = {"test": 0}
    with pytest.raises(ValueError):
        _ = NBTag.from_object(data, schema, name="othername")

    class CustomType:
        def to_nbt(self, name: str = "") -> NBTag:
            return ByteArrayNBT(b"CustomType", name)

    # Wrong data type
    with pytest.raises(TypeError):
        _ = NBTag.from_object(0, CustomType)


def test_to_object_morecases():
    """Test to_object with more edge cases."""

    class CustomType:
        def to_nbt(self, name: str = "") -> NBTag:
            return ByteArrayNBT(b"CustomType", name)

    assert NBTag.from_object(
        {
            "bytearray": b"test",
            "empty_list": [],
            "empty_compound": {},
            "custom": CustomType(),
            "recursive_list": [
                [0, 1, 2],
                [3, 4, 5],
            ],
            "compound_list": [{"test": 0, "test2": 1}, {"test2": 1}],
        },
        {
            "bytearray": ByteArrayNBT,
            "empty_list": [],
            "empty_compound": {},
            "custom": CustomType,
            "recursive_list": [[IntNBT], [ShortNBT]],
            "compound_list": [{"test": ByteNBT, "test2": IntNBT}, {"test2": IntNBT}],
        },
    ).to_object(include_schema=True) == (
        {
            "bytearray": b"test",
            "empty_list": [],
            "empty_compound": {},
            "custom": b"CustomType",
            "recursive_list": [[0, 1, 2], [3, 4, 5]],
            "compound_list": [{"test": 0, "test2": 1}, {"test2": 1}],
        },
        {
            "bytearray": ByteArrayNBT,
            "empty_list": [],
            "empty_compound": {},
            "custom": ByteArrayNBT,  # After the conversion, the NBT tag is a ByteArrayNBT
            "recursive_list": [[IntNBT], [ShortNBT]],
            "compound_list": [{"test": ByteNBT, "test2": IntNBT}, {"test2": IntNBT}],
        },
    )

    assert FloatNBT(0.5).to_object() == 0.5
    assert FloatNBT(0.5, "Hello World").to_object(include_name=True) == {"Hello World": 0.5}
    assert ByteArrayNBT(b"test").to_object() == b"test"  # Do not add name when there is no name
    assert StringNBT("test").to_object() == "test"
    assert StringNBT("test", "name").to_object(include_name=True) == {"name": "test"}
    assert ListNBT([ByteNBT(0), ByteNBT(1)]).to_object() == [0, 1]
    assert ListNBT([ByteNBT(0), ByteNBT(1)], "name").to_object(include_name=True) == {"name": [0, 1]}
    assert IntArrayNBT([0, 1, 2]).to_object() == [0, 1, 2]
    assert LongArrayNBT([0, 1, 2]).to_object() == [0, 1, 2]

    with pytest.raises(TypeError):
        _ = NBTag.to_object(CompoundNBT([]))

    with pytest.raises(TypeError):
        _ = ListNBT([CompoundNBT([]), ListNBT([])]).to_object(include_schema=True)

    with pytest.raises(TypeError):
        _ = ListNBT([IntNBT(0), ShortNBT(0)]).to_object(include_schema=True)


def test_data_conversions():
    """Test data conversions using the built-in functions."""
    assert int(IntNBT(-1)) == -1
    assert float(FloatNBT(0.5)) == 0.5
    assert str(StringNBT("test")) == "test"
    assert bytes(ByteArrayNBT(b"test")) == b"test"
    assert list(ListNBT([ByteNBT(0), ByteNBT(1)])) == [ByteNBT(0), ByteNBT(1)]
    assert dict(CompoundNBT([ByteNBT(0, "first"), ByteNBT(1, "second")])) == {
        "first": ByteNBT(0, "first"),
        "second": ByteNBT(1, "second"),
    }
    assert list(IntArrayNBT([0, 1, 2])) == [0, 1, 2]
    assert list(LongArrayNBT([0, 1, 2])) == [0, 1, 2]


def test_init_nbtag_directly():
    """Test initializing NBTag directly."""
    # TODO: Check if this test really is relevant
    # Isn't this basically just testing stdlib ABCs?
    with pytest.raises(TypeError):
        _ = NBTag(0)  # pyright: ignore[reportAbstractUsage,reportCallIssue] # I know, that's what I'm testing


@pytest.mark.parametrize(
    ("buffer_content", "tag_type"),
    [
        ("01", EndNBT),
        ("00 00", ByteNBT),
        ("01 0000", ShortNBT),
        ("02 00000000", IntNBT),
        ("03 0000000000000000", LongNBT),
        ("04 3F800000", FloatNBT),
        ("05 3FF999999999999A", DoubleNBT),
        ("06 00", ByteArrayNBT),
        ("07 00", StringNBT),
        ("08 00", ListNBT),
        ("09 00", CompoundNBT),
        ("0A 00", IntArrayNBT),
        ("0B 00", LongArrayNBT),
    ],
)
def test_wrong_type(buffer_content: str, tag_type: type[NBTag]):
    """Test read_from with wrong tag type in the buffer."""
    buffer = Buffer(bytearray.fromhex(buffer_content))
    with pytest.raises(TypeError):
        _ = tag_type.read_from(buffer, with_name=False)
