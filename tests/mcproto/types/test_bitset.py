import pytest

from mcproto.buffer import Buffer
from mcproto.types.bitset import Bitset, FixedBitset
from tests.helpers import gen_serializable_test

gen_serializable_test(
    context=globals(),
    cls=FixedBitset.of_size(64),
    fields=[("data", bytearray)],
    serialize_deserialize=[
        ((bytearray(b"\x00\x00\x00\x00\x00\x00\x00\x00"),), b"\x00\x00\x00\x00\x00\x00\x00\x00"),
        ((bytearray(b"\xff\xff\xff\xff\xff\xff\xff\xff"),), b"\xff\xff\xff\xff\xff\xff\xff\xff"),
        ((bytearray(b"\x55\x55\x55\x55\x55\x55\x55\x55"),), b"\x55\x55\x55\x55\x55\x55\x55\x55"),
    ],
)

gen_serializable_test(
    context=globals(),
    cls=FixedBitset.of_size(16),
    fields=[("data", "list[int]")],
    validation_fail=[
        ((bytearray(b"\x00"),), ValueError),
    ],
)

gen_serializable_test(
    context=globals(),
    cls=Bitset,
    fields=[("size", int), ("data", "list[int]")],
    serialize_deserialize=[
        ((1, [1]), b"\x01\x00\x00\x00\x00\x00\x00\x00\x01"),
        (
            (2, [1, -1]),
            b"\x02\x00\x00\x00\x00\x00\x00\x00\x01\xff\xff\xff\xff\xff\xff\xff\xff",
        ),
    ],
    deserialization_fail=[
        (b"\x01", IOError),
    ],
    validation_fail=[
        ((3, [1]), ValueError),
    ],
)


def test_fixed_bitset_no_size():
    """Test FixedBitset exceptions with no size."""
    with pytest.raises(ValueError):
        FixedBitset.from_int(0)

    with pytest.raises(ValueError):
        FixedBitset(bytearray(b""))

    with pytest.raises(ValueError):
        FixedBitset.deserialize(Buffer(b"\x00"))


def test_fixed_bitset_indexing():
    """Test indexing and setting values in a FixedBitset."""
    b = FixedBitset.of_size(12).from_int(0)
    assert b[0] is False
    assert b[12] is False

    b[0] = True
    assert b[0] is True
    assert b[12] is False

    b[12] = True
    assert b[12] is True
    assert b[0] is True

    b[0] = False
    assert b[0] is False
    assert b[12] is True


def test_bitset_indexing():
    """Test indexing and setting values in a Bitset."""
    b = Bitset.from_int(0, size=2)
    assert b[0] is False
    assert b[127] is False

    b[0] = True
    assert b[0] is True

    b[127] = True
    assert b[127] is True

    b[0] = False
    assert b[0] is False


def test_fixed_bitset_and():
    """Test bitwise AND operation between FixedBitsets."""
    b1 = FixedBitset.of_size(64).from_int(-1)
    b2 = FixedBitset.of_size(64).from_int(0)

    result = b1 & b2
    assert bytes(result) == b"\x00\x00\x00\x00\x00\x00\x00\x00"


def test_bitset_and():
    """Test bitwise AND operation between Bitsets."""
    b1 = Bitset(2, [0x0101010101010101, 0x0101010101010100])
    b2 = Bitset(2, [1, 1])

    result = b1 & b2
    assert result == Bitset(2, [1, 0])


def test_fixed_bitset_or():
    """Test bitwise OR operation between FixedBitsets."""
    b1 = FixedBitset.of_size(8).from_int(-2)
    b2 = FixedBitset.of_size(8).from_int(0x01)

    result = b1 | b2
    assert bytes(result) == b"\xff"


def test_bitset_or():
    """Test bitwise OR operation between Bitsets."""
    b1 = Bitset(2, [0x0101010101010101, 0x0101010101010100])
    b2 = Bitset(2, [1, 1])

    result = b1 | b2
    assert bytes(result) == b"\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01"


def test_fixed_bitset_xor():
    """Test bitwise XOR operation between FixedBitsets."""
    b1 = FixedBitset.of_size(64)(bytearray(b"\xff\xff\xff\xff\xff\xff\xff\xff"))
    b2 = FixedBitset.of_size(64)(bytearray(b"\x00\x00\x00\x00\x00\x00\x00\x00"))

    result = b1 ^ b2
    assert result == FixedBitset.of_size(64).from_int(-1)


def test_bitset_xor():
    """Test bitwise XOR operation between Bitsets."""
    b1 = Bitset(2, [0x0101010101010101, 0x0101010101010101])
    b2 = Bitset(2, [0, 0])

    result = b1 ^ b2
    assert result == Bitset(2, [0x0101010101010101, 0x0101010101010101])


def test_fixed_bitset_invert():
    """Test bitwise inversion operation on FixedBitsets."""
    b = FixedBitset.of_size(64)(bytearray(b"\xff\xff\xff\xff\xff\xff\xff\xff"))

    inverted = ~b
    assert inverted == FixedBitset.of_size(64).from_int(0)


def test_bitset_invert():
    """Test bitwise inversion operation on Bitsets."""
    b = Bitset(2, [0, 0])

    inverted = ~b
    assert inverted == Bitset(2, [-1, -1])


def test_fixed_bitset_size_undefined():
    """Test that FixedBitset raises ValueError when size is not defined."""
    with pytest.raises(ValueError):
        FixedBitset.from_int(0)

    with pytest.raises(ValueError):
        FixedBitset(bytearray(b"\x00\x00\x00\x00"))

    with pytest.raises(ValueError):
        FixedBitset.deserialize(Buffer(b"\x00"))


def test_bitset_len():
    """Test that FixedBitset has the correct length."""
    b = FixedBitset.of_size(64).from_int(0)
    assert len(b) == 64

    b = FixedBitset.of_size(8).from_int(0)
    assert len(b) == 8

    b = Bitset(2, [0, 0])
    assert len(b) == 128


def test_fixed_bitset_operations_length_mismatch():
    """Test that FixedBitset operations raise ValueError when lengths don't match."""
    b1 = FixedBitset.of_size(64).from_int(0)
    b2 = FixedBitset.of_size(8).from_int(0)
    b3 = "not a bitset"

    with pytest.raises(ValueError):
        b1 & b2  # type: ignore

    with pytest.raises(ValueError):
        b1 | b2  # type: ignore

    with pytest.raises(ValueError):
        b1 ^ b2  # type: ignore

    assert b1 != b3


def test_bitset_operations_length_mismatch():
    """Test that Bitset operations raise ValueError when lengths don't match."""
    b1 = Bitset(2, [0, 0])
    b2 = Bitset.from_int(1)
    b3 = "not a bitset"

    with pytest.raises(ValueError):
        b1 & b2  # type: ignore

    with pytest.raises(ValueError):
        b1 | b2  # type: ignore

    with pytest.raises(ValueError):
        b1 ^ b2  # type: ignore

    assert b1 != b3


def test_fixed_bitset_cache():
    """Test that FixedBitset.of_size caches the result."""
    b1 = FixedBitset.of_size(64)
    for i in range(1, 64):
        b = FixedBitset.of_size(i)
        assert b is not b1
    b2 = FixedBitset.of_size(64)

    assert b1 is b2
