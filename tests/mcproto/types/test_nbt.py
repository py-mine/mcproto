from __future__ import annotations

import struct
from typing import Any, Dict, List, cast

import pytest

from mcproto.buffer import Buffer
from mcproto.types.nbt import (
    ByteArrayNBT,
    ByteNBT,
    CompoundNBT,
    DoubleNBT,
    EndNBT,
    FloatNBT,
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
    test_data=[
        ((), b"\x00"),
        (IOError, b"\x01"),
    ],
)


# endregion
# region Numerical NBT tests

gen_serializable_test(
    context=globals(),
    cls=ByteNBT,
    fields=[("payload", int), ("name", str)],
    test_data=[
        ((0, "a"), b"\x01\x00\x01a\x00"),
        ((1, "test"), b"\x01\x00\x04test\x01"),
        ((127, "&à@é"), b"\x01\x00\x06" + bytes("&à@é", "utf-8") + b"\x7F"),
        ((-128, "test"), b"\x01\x00\x04test\x80"),
        ((-1, "a" * 100), b"\x01\x00\x64" + b"a" * 100 + b"\xFF"),
        # Errors
        (IOError, b"\x01\x00\x04test"),
        (IOError, b"\x01\x00\x04tes"),
        (IOError, b"\x01\x00"),
        (IOError, b"\x01"),
        # Wrong type
        (TypeError, b"\x02\x00\x01a\x00"),
        (TypeError, b"\xff\x00\x01a\x00"),
        # Out of bounds
        ((1 << 7, "a"), OverflowError),
        ((-(1 << 7) - 1, "a"), OverflowError),
        ((1 << 8, "a"), OverflowError),
        ((-(1 << 8) - 1, "a"), OverflowError),
        ((1000, "a"), OverflowError),
    ],
)

gen_serializable_test(
    context=globals(),
    cls=ShortNBT,
    fields=[("payload", int), ("name", str)],
    test_data=[
        ((0, "a"), b"\x02\x00\x01a\x00\x00"),
        ((1, "test"), b"\x02\x00\x04test\x00\x01"),
        ((32767, "&à@é"), b"\x02\x00\x06" + bytes("&à@é", "utf-8") + b"\x7F\xFF"),
        ((-32768, "test"), b"\x02\x00\x04test\x80\x00"),
        ((-1, "a" * 100), b"\x02\x00\x64" + b"a" * 100 + b"\xFF\xFF"),
        # Errors
        (IOError, b"\x02\x00\x04test"),
        (IOError, b"\x02\x00\x04tes"),
        (IOError, b"\x02\x00"),
        (IOError, b"\x02"),
        # Out of bounds
        ((1 << 15, "a"), OverflowError),
        ((-(1 << 15) - 1, "a"), OverflowError),
        ((1 << 16, "a"), OverflowError),
        ((-(1 << 16) - 1, "a"), OverflowError),
        ((1e10, "a"), OverflowError),
    ],
)

gen_serializable_test(
    context=globals(),
    cls=IntNBT,
    fields=[("payload", int), ("name", str)],
    test_data=[
        ((0, "a"), b"\x03\x00\x01a\x00\x00\x00\x00"),
        ((1, "test"), b"\x03\x00\x04test\x00\x00\x00\x01"),
        ((2147483647, "&à@é"), b"\x03\x00\x06" + bytes("&à@é", "utf-8") + b"\x7F\xFF\xFF\xFF"),
        ((-2147483648, "test"), b"\x03\x00\x04test\x80\x00\x00\x00"),
        ((-1, "a" * 100), b"\x03\x00\x64" + b"a" * 100 + b"\xFF\xFF\xFF\xFF"),
        # Errors
        (IOError, b"\x03\x00\x04test"),
        (IOError, b"\x03\x00\x04tes"),
        (IOError, b"\x03\x00"),
        (IOError, b"\x03"),
        # Out of bounds
        ((1 << 31, "a"), OverflowError),
        ((-(1 << 31) - 1, "a"), OverflowError),
        ((1 << 32, "a"), OverflowError),
        ((-(1 << 32) - 1, "a"), OverflowError),
        ((1e50, "a"), OverflowError),
    ],
)

gen_serializable_test(
    context=globals(),
    cls=LongNBT,
    fields=[("payload", int), ("name", str)],
    test_data=[
        ((0, "a"), b"\x04\x00\x01a\x00\x00\x00\x00\x00\x00\x00\x00"),
        ((1, "test"), b"\x04\x00\x04test\x00\x00\x00\x00\x00\x00\x00\x01"),
        (((1 << 63) - 1, "&à@é"), b"\x04\x00\x06" + bytes("&à@é", "utf-8") + b"\x7F\xFF\xFF\xFF\xFF\xFF\xFF\xFF"),
        ((-1 << 63, "test"), b"\x04\x00\x04test\x80\x00\x00\x00\x00\x00\x00\x00"),
        ((-1, "a" * 100), b"\x04\x00\x64" + b"a" * 100 + b"\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF"),
        # Errors
        (IOError, b"\x04\x00\x04test"),
        (IOError, b"\x04\x00\x04tes"),
        (IOError, b"\x04\x00"),
        (IOError, b"\x04"),
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
    test_data=[
        ((1.0, "a"), b"\x05\x00\x01a" + bytes(struct.pack(">f", 1.0))),
        ((3.14, "test"), b"\x05\x00\x04test" + bytes(struct.pack(">f", 3.14))),
        ((-1.0, "&à@é"), b"\x05\x00\x06" + bytes("&à@é", "utf-8") + bytes(struct.pack(">f", -1.0))),
        ((12.0, "a" * 100), b"\x05\x00\x64" + b"a" * 100 + bytes(struct.pack(">f", 12.0))),
        # Errors
        (IOError, b"\x05\x00\x04test"),
        (IOError, b"\x05\x00\x04tes"),
        (IOError, b"\x05\x00"),
        (IOError, b"\x05"),
    ],
)

gen_serializable_test(
    context=globals(),
    cls=DoubleNBT,
    fields=[("payload", float), ("name", str)],
    test_data=[
        ((1.0, "a"), b"\x06\x00\x01a" + bytes(struct.pack(">d", 1.0))),
        ((3.14, "test"), b"\x06\x00\x04test" + bytes(struct.pack(">d", 3.14))),
        ((-1.0, "&à@é"), b"\x06\x00\x06" + bytes("&à@é", "utf-8") + bytes(struct.pack(">d", -1.0))),
        ((12.0, "a" * 100), b"\x06\x00\x64" + b"a" * 100 + bytes(struct.pack(">d", 12.0))),
        # Errors
        (IOError, b"\x06\x00\x04test\x01"),
        (IOError, b"\x06\x00\x04test"),
        (IOError, b"\x06\x00\x04tes"),
        (IOError, b"\x06\x00"),
        (IOError, b"\x06"),
    ],
)
# endregion
# region Variable Length NBT tests
gen_serializable_test(
    context=globals(),
    cls=ByteArrayNBT,
    fields=[("payload", bytes), ("name", str)],
    test_data=[
        ((b"", "a"), b"\x07\x00\x01a\x00\x00\x00\x00"),
        ((b"\x00", "test"), b"\x07\x00\x04test\x00\x00\x00\x01\x00"),
        ((b"\x00\x01", "&à@é"), b"\x07\x00\x06" + bytes("&à@é", "utf-8") + b"\x00\x00\x00\x02\x00\x01"),
        ((b"\x00\x01\x02", "test"), b"\x07\x00\x04test\x00\x00\x00\x03\x00\x01\x02"),
        ((b"\xFF" * 1024, "a" * 100), b"\x07\x00\x64" + b"a" * 100 + b"\x00\x00\x04\x00" + b"\xFF" * 1024),
        ((b"Hello World", "test"), b"\x07\x00\x04test\x00\x00\x00\x0B" + b"Hello World"),
        # Errors
        (IOError, b"\x07\x00\x04test"),
        (IOError, b"\x07\x00\x04tes"),
        (IOError, b"\x07\x00"),
        (IOError, b"\x07"),
        (IOError, b"\x07\x00\x01a\x00\x01"),
        (IOError, b"\x07\x00\x01a\x00\x00\x00\xFF"),
        # Negative length
        (ValueError, b"\x07\x00\x01a\xFF\xFF\xFF\xFF"),
    ],
)

gen_serializable_test(
    context=globals(),
    cls=StringNBT,
    fields=[("payload", str), ("name", str)],
    test_data=[
        (("", "a"), b"\x08\x00\x01a\x00\x00"),
        (("test", "a"), b"\x08\x00\x01a\x00\x04" + b"test"),
        (("a" * 100, "&à@é"), b"\x08\x00\x06" + bytes("&à@é", "utf-8") + b"\x00\x64" + b"a" * 100),
        (("&à@é", "test"), b"\x08\x00\x04test\x00\x06" + bytes("&à@é", "utf-8")),
        # Errors
        (IOError, b"\x08\x00\x04test"),
        (IOError, b"\x08\x00\x04tes"),
        (IOError, b"\x08\x00"),
        (IOError, b"\x08"),
        # Negative length
        (ValueError, b"\x08\xFF\xFF\xFF\xFF"),
        # Unicode decode error
        (UnicodeDecodeError, b"\x08\x00\x01a\x00\x01\xFF"),
        # String too long
        (("a" * 32768, "b"), ValueError),
    ],
)

gen_serializable_test(
    context=globals(),
    cls=ListNBT,
    fields=[("payload", list), ("name", str)],
    test_data=[
        # Here we only want to test ListNBT related stuff
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
        # Errors
        # Not enough data
        (IOError, b"\x09\x00\x01a"),
        (IOError, b"\x09\x00\x01a\x01"),
        (IOError, b"\x09\x00\x01a\x01\x00"),
        (IOError, b"\x09\x00\x01a\x01\x00\x00\x00\x01"),
        (IOError, b"\x09\x00\x01a\x01\x00\x00\x00\x03\x01"),
        # Invalid tag type
        (TypeError, b"\x09\x00\x01a\xff\x00\x00\x01\x00"),
        # Not NBTags
        (([1, 2, 3], "a"), TypeError),
        # Not the same tag type
        (([ByteNBT(0), IntNBT(0)], "a"), TypeError),
        # Contains named tags
        (([ByteNBT(0, name="Byte")], "a"), ValueError),
    ],
)

gen_serializable_test(
    context=globals(),
    cls=CompoundNBT,
    fields=[("payload", list), ("name", str)],
    test_data=[
        (([], "a"), b"\x0A\x00\x01a\x00"),
        (([ByteNBT(0, name="Byte")], "a"), b"\x0A\x00\x01a" + ByteNBT(0, name="Byte").serialize() + b"\x00"),
        (
            ([ShortNBT(128, "Short"), ByteNBT(-1, "Byte")], "a"),
            b"\x0A\x00\x01a" + ShortNBT(128, "Short").serialize() + ByteNBT(-1, "Byte").serialize() + b"\x00",
        ),
        (
            ([CompoundNBT([ByteNBT(0, name="Byte")], name="test")], "a"),
            b"\x0A\x00\x01a" + CompoundNBT([ByteNBT(0, name="Byte")], "test").serialize() + b"\x00",
        ),
        (
            ([ListNBT([ByteNBT(0)] * 3, name="List")], "a"),
            b"\x0A\x00\x01a" + ListNBT([ByteNBT(0)] * 3, name="List").serialize() + b"\x00",
        ),
        # Errors
        # Not enough data
        (IOError, b"\x0A\x00\x01a"),
        (IOError, b"\x0A\x00\x01a\x01"),
        # All muse be NBTags
        (([0, 1, 2], "a"), TypeError),
        # All with a name
        (([ByteNBT(0)], "a"), ValueError),
        # Must be unique
        (([ByteNBT(0, name="Byte"), ByteNBT(0, name="Byte")], "a"), ValueError),
    ],
)

gen_serializable_test(
    context=globals(),
    cls=IntArrayNBT,
    fields=[("payload", list), ("name", str)],
    test_data=[
        (([], "a"), b"\x0B\x00\x01a\x00\x00\x00\x00"),
        (([0], "a"), b"\x0B\x00\x01a\x00\x00\x00\x01\x00\x00\x00\x00"),
        (([0, 1], "a"), b"\x0B\x00\x01a\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x01"),
        (([1, 2, 3], "a"), b"\x0B\x00\x01a\x00\x00\x00\x03\x00\x00\x00\x01\x00\x00\x00\x02\x00\x00\x00\x03"),
        (([(1 << 31) - 1], "a"), b"\x0B\x00\x01a\x00\x00\x00\x01\x7F\xFF\xFF\xFF"),
        (([-1, -2, -3], "a"), b"\x0B\x00\x01a\x00\x00\x00\x03\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFE\xFF\xFF\xFF\xFD"),
        # Errors
        # Not enough data
        (IOError, b"\x0B\x00\x01a"),
        (IOError, b"\x0B\x00\x01a\x01"),
        (IOError, b"\x0B\x00\x01a\x00\x00\x00\x01"),
        (IOError, b"\x0B\x00\x01a\x00\x00\x00\x03\x01"),
        # Must contain ints only
        ((["a"], "a"), TypeError),
        (([IntNBT(0)], "a"), TypeError),
        (([1 << 31], "a"), OverflowError),
        (([-(1 << 31) - 1], "a"), OverflowError),
    ],
)
gen_serializable_test(
    context=globals(),
    cls=LongArrayNBT,
    fields=[("payload", list), ("name", str)],
    test_data=[
        (([], "a"), b"\x0C\x00\x01a\x00\x00\x00\x00"),
        (([0], "a"), b"\x0C\x00\x01a\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00"),
        (
            ([0, 1], "a"),
            b"\x0C\x00\x01a\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01",
        ),
        (([(1 << 63) - 1], "a"), b"\x0C\x00\x01a\x00\x00\x00\x01\x7F\xFF\xFF\xFF\xFF\xFF\xFF\xFF"),
        (
            ([-1, -2], "a"),
            b"\x0C\x00\x01a\x00\x00\x00\x02\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFE",
        ),
        # Not enough data
        (IOError, b"\x0C\x00\x01a"),
        (IOError, b"\x0C\x00\x01a\x01"),
        (IOError, b"\x0C\x00\x01a\x00\x00\x00\x01"),
        (IOError, b"\x0C\x00\x01a\x00\x00\x00\x03\x01"),
        # Must contain ints only
        ((["a"], "a"), TypeError),
        (([LongNBT(0)], "a"), TypeError),
        (([1 << 63], "a"), OverflowError),
        (([-(1 << 63) - 1], "a"), OverflowError),
    ],
)

# endregion


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
    buffer = Buffer(b"\x0B\x00\x01a\xFF\xFF\xFF\xFF")
    assert IntArrayNBT.read_from(buffer) == IntArrayNBT([], "a")


# region NBTag


def test_nbt_helloworld():
    """Test serialization/deserialization of a simple NBT tag.

    Source data: https://wiki.vg/NBT#Example.
    """
    data = bytearray.fromhex("0a000b68656c6c6f20776f726c640800046e616d65000942616e616e72616d6100")
    buffer = Buffer(data)

    expected_object = {
        "hello world": {
            "name": "Bananrama",
        }
    }

    data = NBTag.read_from(buffer)
    assert data == NBTag.from_object(expected_object)
    assert data.to_object() == expected_object


def test_nbt_bigfile():
    """Test serialization/deserialization of a big NBT tag.

    Slighly modified from the source data to also include a IntArrayNBT and a LongArrayNBT.
    Source data: https://wiki.vg/NBT#Example.
    """
    data = "0a00054c6576656c0400086c6f6e67546573747fffffffffffffff02000973686f7274546573747fff08000a737472696e6754657374002948454c4c4f20574f524c4420544849532049532041205445535420535452494e4720c385c384c39621050009666c6f6174546573743eff1832030007696e74546573747fffffff0a00146e657374656420636f6d706f756e6420746573740a000368616d0800046e616d65000648616d70757305000576616c75653f400000000a00036567670800046e616d6500074567676265727405000576616c75653f00000000000c000f6c6973745465737420286c6f6e672900000005000000000000000b000000000000000c000000000000000d000000000000000e7fffffffffffffff0b000e6c697374546573742028696e7429000000047fffffff7ffffffe7ffffffd7ffffffc0900136c697374546573742028636f6d706f756e64290a000000020800046e616d65000f436f6d706f756e642074616720233004000a637265617465642d6f6e000001265237d58d000800046e616d65000f436f6d706f756e642074616720233104000a637265617465642d6f6e000001265237d58d0001000862797465546573747f07006562797465417272617954657374202874686520666972737420313030302076616c756573206f6620286e2a6e2a3235352b6e2a3729253130302c207374617274696e672077697468206e3d302028302c2036322c2033342c2031362c20382c202e2e2e2929000003e8003e2210080a162c4c12462004564e505c0e2e5828024a3830323e54103a0a482c1a12142036561c502a0e60585a02183862320c54423a3c485e1a44145236241c1e2a4060265a34180662000c2242083c165e4c44465204244e1e5c402e2628344a0630003e2210080a162c4c12462004564e505c0e2e5828024a3830323e54103a0a482c1a12142036561c502a0e60585a02183862320c54423a3c485e1a44145236241c1e2a4060265a34180662000c2242083c165e4c44465204244e1e5c402e2628344a0630003e2210080a162c4c12462004564e505c0e2e5828024a3830323e54103a0a482c1a12142036561c502a0e60585a02183862320c54423a3c485e1a44145236241c1e2a4060265a34180662000c2242083c165e4c44465204244e1e5c402e2628344a0630003e2210080a162c4c12462004564e505c0e2e5828024a3830323e54103a0a482c1a12142036561c502a0e60585a02183862320c54423a3c485e1a44145236241c1e2a4060265a34180662000c2242083c165e4c44465204244e1e5c402e2628344a0630003e2210080a162c4c12462004564e505c0e2e5828024a3830323e54103a0a482c1a12142036561c502a0e60585a02183862320c54423a3c485e1a44145236241c1e2a4060265a34180662000c2242083c165e4c44465204244e1e5c402e2628344a0630003e2210080a162c4c12462004564e505c0e2e5828024a3830323e54103a0a482c1a12142036561c502a0e60585a02183862320c54423a3c485e1a44145236241c1e2a4060265a34180662000c2242083c165e4c44465204244e1e5c402e2628344a0630003e2210080a162c4c12462004564e505c0e2e5828024a3830323e54103a0a482c1a12142036561c502a0e60585a02183862320c54423a3c485e1a44145236241c1e2a4060265a34180662000c2242083c165e4c44465204244e1e5c402e2628344a0630003e2210080a162c4c12462004564e505c0e2e5828024a3830323e54103a0a482c1a12142036561c502a0e60585a02183862320c54423a3c485e1a44145236241c1e2a4060265a34180662000c2242083c165e4c44465204244e1e5c402e2628344a0630003e2210080a162c4c12462004564e505c0e2e5828024a3830323e54103a0a482c1a12142036561c502a0e60585a02183862320c54423a3c485e1a44145236241c1e2a4060265a34180662000c2242083c165e4c44465204244e1e5c402e2628344a0630003e2210080a162c4c12462004564e505c0e2e5828024a3830323e54103a0a482c1a12142036561c502a0e60585a02183862320c54423a3c485e1a44145236241c1e2a4060265a34180662000c2242083c165e4c44465204244e1e5c402e2628344a063005000a646f75626c65546573743efc7b5e00"  # noqa: E501
    data = bytearray.fromhex(data)
    buffer = Buffer(data)

    expected_object = {
        "Level": {
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
            "byteArrayTest (the first 1000 values of (n*n*255+n*7)%100"
            ", starting with n=0 (0, 62, 34, 16, 8, ...))": bytes((n * n * 255 + n * 7) % 100 for n in range(1000)),
            "doubleTest": 0.4931287132182315,
        }
    }

    data = CompoundNBT.deserialize(buffer)
    # print(f"{data=}\n{expected_object=}\n{data.to_object()=}\n{NBTag.from_object(expected_object)=}")

    def check_equality(self: Any, other: Any) -> bool:
        """Check if two objects are equal, with deep epsilon check for floats."""
        if type(self) != type(other):
            return False
        if isinstance(self, dict):
            self = cast(Dict[str, Any], self)
            if len(self) != len(other):
                return False
            for key in self:
                if key not in other:
                    return False
                if not check_equality(self[key], other[key]):
                    return False
            return True
        if isinstance(self, list):
            self = cast(List[Any], self)
            if len(self) != len(other):
                return False
            return all(check_equality(self[i], other[i]) for i in range(len(self)))
        if isinstance(self, float):
            return abs(self - other) < 1e-6
        if self != other:
            return False
        return self == other

    assert data == NBTag.from_object(expected_object)
    assert check_equality(data.to_object(), expected_object)


# endregion
# region Edge cases


def test_from_object_out_of_bounds():
    """Test from_object with a value that is out of bounds."""
    with pytest.raises(ValueError):
        NBTag.from_object({"test": 1 << 63})

    with pytest.raises(ValueError):
        NBTag.from_object({"test": -(1 << 63) - 1})

    with pytest.raises(ValueError):
        NBTag.from_object({"test": [1 << 63]})

    with pytest.raises(ValueError):
        NBTag.from_object({"test": [-(1 << 63) - 1]})


def test_from_object_morecases():
    """Test from_object with more edge cases."""

    class CustomType:
        def __bytes__(self):
            return b"test"

    assert NBTag.from_object(
        {
            "nbtag": ByteNBT(0),  # ByteNBT
            "bytearray": b"test",  # Conversion from bytes
            "empty_list": [],  # Empty list with type EndNBT
            "empty_compound": {},  # Empty compound
            "custom": CustomType(),  # Custom type with __bytes__ method
        }
    ) == CompoundNBT(
        [  # Order is shuffled because the spec does not require a specific order
            CompoundNBT([], "empty_compound"),
            ByteArrayNBT(b"test", "bytearray"),
            ByteArrayNBT(b"test", "custom"),
            ListNBT([], "empty_list"),
            ByteNBT(0, "nbtag"),
        ]
    )

    # Not a valid object
    with pytest.raises(TypeError):
        NBTag.from_object({"test": object()})

    # List with different types
    with pytest.raises(TypeError):
        NBTag.from_object([1, "test"])

    compound = CompoundNBT.from_object(
        {
            "test": ByteNBT(0),
            "test2": IntNBT(0),
        },
        name="compound",
    )
    assert NBTag.__eq__(compound["test"], ByteNBT(0, "test"))  # type:ignore
    assert compound["test2"] == IntNBT(0, "test2")
    with pytest.raises(KeyError):
        compound["test3"]

    # Cannot index into a ByteNBT
    with pytest.raises(TypeError):
        compound["test"][0]  # type:ignore

    listnbt = ListNBT.from_object([0, 1, 2], use_int_array=False)
    assert listnbt[0] == ByteNBT(0)
    assert listnbt[1] == ByteNBT(1)
    assert listnbt[2] == ByteNBT(2)
    with pytest.raises(IndexError):
        listnbt[3]
    with pytest.raises(TypeError):
        listnbt["hello"]

    assert listnbt[-1] == ByteNBT(2)
    assert listnbt[-2] == ByteNBT(1)
    assert listnbt[-3] == ByteNBT(0)

    with pytest.raises(TypeError):
        listnbt[object()]  # type:ignore

    assert listnbt.value == [0, 1, 2]
    assert listnbt.to_object() == [0, 1, 2]
    assert ListNBT([]).value == []
    assert compound.to_object() == {"compound": {"test": 0, "test2": 0}}
    assert compound.value == {"test": 0, "test2": 0}
    assert ListNBT([IntNBT(0)]).value == [0]

    assert NBTag.from_object(bytearray(b"test")) == ByteArrayNBT(b"test")


def test_value_property():
    """Test the value property of the NBT tags."""
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


def test_to_object_morecases():
    """Test to_object with more edge cases."""

    class CustomType:
        def __bytes__(self):
            return b"test"

    assert NBTag.from_object(
        {
            "bytearray": b"test",
            "empty_list": [],
            "empty_compound": {},
            "custom": CustomType(),
        }
    ).to_object() == {
        "bytearray": b"test",
        "empty_list": [],
        "empty_compound": {},
        "custom": b"test",
    }

    assert NBTag.to_object(CompoundNBT([])) == {}

    assert EndNBT().to_object() == {}  # Does not add anything when doing dict.update
    assert FloatNBT(0.5).to_object() == 0.5
    assert FloatNBT(0.5, "Hello World").to_object() == {"Hello World": 0.5}
    assert ByteArrayNBT(b"test").to_object() == b"test"  # Do not add name when there is no name
    assert StringNBT("test").to_object() == "test"
    assert StringNBT("test", "name").to_object() == {"name": "test"}
    assert ListNBT([ByteNBT(0), ByteNBT(1)]).to_object() == [0, 1]
    assert ListNBT([ByteNBT(0), ByteNBT(1)], "name").to_object() == {"name": [0, 1]}
    assert IntArrayNBT([0, 1, 2]).to_object() == [0, 1, 2]
    assert LongArrayNBT([0, 1, 2]).to_object() == [0, 1, 2]


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


@pytest.mark.parametrize(
    "cls",
    [
        ByteNBT,
        ShortNBT,
        IntNBT,
        LongNBT,
        FloatNBT,
        DoubleNBT,
        ByteArrayNBT,
        StringNBT,
        ListNBT,
        CompoundNBT,
        IntArrayNBT,
        LongArrayNBT,
    ],
)
def test_invalid_type_in_buffer(cls: type[NBTag]):
    """Test invalid types in the buffer."""
    wrong_data = b"\x00\x00\x00\x00"
    buffer = Buffer(wrong_data)
    with pytest.raises(TypeError):
        cls.read_from(buffer)
    buffer = Buffer(wrong_data)
    with pytest.raises(TypeError):
        cls.deserialize(buffer)


def test_invalid_type_in_buffer_end():
    """Test invalid types in the buffer."""
    wrong_data = b"\x01\x00\x00\x00"
    buffer = Buffer(wrong_data)
    with pytest.raises(TypeError):
        EndNBT.read_from(buffer)
    buffer = Buffer(wrong_data)
    with pytest.raises(TypeError):
        EndNBT.deserialize(buffer)
