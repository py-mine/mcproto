from __future__ import annotations

import struct
from typing import cast
import pytest
import math

from mcproto.buffer import Buffer
from mcproto.types.vec3 import Position, Vec3
from tests.helpers import gen_serializable_test

gen_serializable_test(
    context=globals(),
    cls=Position,
    fields=[("x", int), ("y", int), ("z", int)],
    serialize_deserialize=[
        ((0, 0, 0), b"\x00\x00\x00\x00\x00\x00\x00\x00"),
        ((-1, -1, -1), b"\xff\xff\xff\xff\xff\xff\xff\xff"),
        # from https://wiki.vg/Protocol#Position
        (
            (18357644, 831, -20882616),
            bytes([0b01000110, 0b00000111, 0b01100011, 0b00101100, 0b00010101, 0b10110100, 0b10000011, 0b00111111]),
        ),
    ],
    validation_fail=[
        # X out of bounds
        ((1 << 25, 0, 0), OverflowError),
        ((-(1 << 25) - 1, 0, 0), OverflowError),
        # Y out of bounds
        ((0, 1 << 11, 0), OverflowError),
        ((0, -(1 << 11) - 1, 0), OverflowError),
        # Z out of bounds
        ((0, 0, 1 << 25), OverflowError),
        ((0, 0, -(1 << 25) - 1), OverflowError),
    ],
)

gen_serializable_test(
    context=globals(),
    cls=Vec3,
    fields=[("x", float), ("y", float), ("z", float)],
    serialize_deserialize=[
        ((0.0, 0.0, 0.0), struct.pack(">fff", 0.0, 0.0, 0.0)),
        ((-1.0, -1.0, -1.0), struct.pack(">fff", -1.0, -1.0, -1.0)),
        ((1.0, 2.0, 3.0), struct.pack(">fff", 1.0, 2.0, 3.0)),
        ((1.5, 2.5, 3.5), struct.pack(">fff", 1.5, 2.5, 3.5)),
    ],
    validation_fail=[
        # Invalid values
        ((1.0, 2.0, "3.0"), TypeError),
        ((float("nan"), 2.0, 3.0), ValueError),
        ((1.0, float("inf"), 3.0), ValueError),
        ((1.0, 2.0, -float("inf")), ValueError),
    ],
)


def test_position_addition():
    """Test that two Position objects can be added together (resuling in a new Position object)."""
    p1 = Position(x=1, y=2, z=3)
    p2 = Position(x=4, y=5, z=6)
    p3 = p1 + p2
    assert type(p3) == Position
    assert p3.x == 5
    assert p3.y == 7
    assert p3.z == 9


def test_position_subtraction():
    """Test that two Position objects can be subtracted (resuling in a new Position object)."""
    p1 = Position(x=1, y=2, z=3)
    p2 = Position(x=2, y=4, z=6)
    p3 = p2 - p1
    assert type(p3) == Position
    assert p3.x == 1
    assert p3.y == 2
    assert p3.z == 3


def test_position_negative():
    """Test that a Position object can be negated."""
    p1 = Position(x=1, y=2, z=3)
    p2 = -p1
    assert type(p2) == Position
    assert p2.x == -1
    assert p2.y == -2
    assert p2.z == -3


def test_position_multiplication_int():
    """Test that a Position object can be multiplied by an integer."""
    p1 = Position(x=1, y=2, z=3)
    p2 = p1 * 2
    assert p2.x == 2
    assert p2.y == 4
    assert p2.z == 6


def test_position_multiplication_float():
    """Test that a Position object can be multiplied by a float."""
    p1 = Position(x=2, y=4, z=6)
    p2 = p1 * 1.5
    assert type(p2) == Position
    assert p2.x == 3
    assert p2.y == 6
    assert p2.z == 9


def test_vec3_to_position():
    """Test that a Vec3 object can be converted to a Position object."""
    v = Vec3(x=1.5, y=2.5, z=3.5)
    p = v.to_position()
    assert type(p) == Position
    assert p.x == 1
    assert p.y == 2
    assert p.z == 3


def test_position_to_vec3():
    """Test that a Position object can be converted to a Vec3 object."""
    p = Position(x=1, y=2, z=3)
    v = p.to_vec3()
    assert type(v) == Vec3
    assert v.x == 1.0
    assert v.y == 2.0
    assert v.z == 3.0


def test_position_to_tuple():
    """Test that a Position object can be converted to a tuple."""
    p = Position(x=1, y=2, z=3)
    t = p.to_tuple()
    assert type(t) == tuple
    assert t == (1, 2, 3)


def test_vec3_addition():
    """Test that two Vec3 objects can be added together (resuling in a new Vec3 object)."""
    v1 = Vec3(x=1.0, y=2.0, z=3.0)
    v2 = Vec3(x=4.5, y=5.25, z=6.125)
    v3 = v1 + v2
    assert type(v3) == Vec3
    assert v3.x == 5.5
    assert v3.y == 7.25
    assert v3.z == 9.125


def test_vec3_subtraction():
    """Test that two Vec3 objects can be subtracted (resuling in a new Vec3 object)."""
    v1 = Vec3(x=1.0, y=2.0, z=3.0)
    v2 = Vec3(x=4.5, y=5.25, z=6.125)
    v3 = v2 - v1
    assert type(v3) == Vec3
    assert v3.x == 3.5
    assert v3.y == 3.25
    assert v3.z == 3.125


def test_vec3_negative():
    """Test that a Vec3 object can be negated."""
    v1 = Vec3(x=1.0, y=2.5, z=3.0)
    v2 = -v1
    assert type(v2) == Vec3
    assert v2.x == -1.0
    assert v2.y == -2.5
    assert v2.z == -3.0


def test_vec3_multiplication_int():
    """Test that a Vec3 object can be multiplied by an integer."""
    v1 = Vec3(x=1.0, y=2.25, z=3.0)
    v2 = v1 * 2
    assert v2.x == 2.0
    assert v2.y == 4.5
    assert v2.z == 6.0


def test_vec3_multiplication_float():
    """Test that a Vec3 object can be multiplied by a float."""
    v1 = Vec3(x=2.0, y=4.5, z=6.0)
    v2 = v1 * 1.5
    assert type(v2) == Vec3
    assert v2.x == 3.0
    assert v2.y == 6.75
    assert v2.z == 9.0


def test_vec3_norm_squared():
    """Test that the squared norm of a Vec3 object can be calculated."""
    v = Vec3(x=3.0, y=4.0, z=5.0)
    assert v.norm_squared() == 50.0


def test_vec3_norm():
    """Test that the norm of a Vec3 object can be calculated."""
    v = Vec3(x=3.0, y=4.0, z=5.0)
    assert (v.norm() - 50.0**0.5) < 1e-6


@pytest.mark.parametrize(
    ("x", "y", "z", "expected"),
    [
        (0, 0, 0, ZeroDivisionError),
        (1, 0, 0, Vec3(x=1, y=0, z=0)),
        (0, 1, 0, Vec3(x=0, y=1, z=0)),
        (0, 0, 1, Vec3(x=0, y=0, z=1)),
        (1, 1, 1, Vec3(x=1, y=1, z=1) / math.sqrt(3)),
        (-1, -1, -1, Vec3(x=-1, y=-1, z=-1) / math.sqrt(3)),
    ],
)
def test_vec3_normalize(x: float, y: float, z: float, expected: Vec3 | type):
    """Test that a Vec3 object can be normalized."""
    v = Vec3(x=x, y=y, z=z)
    if isinstance(expected, type):
        expected = cast("type[Exception]", expected)
        with pytest.raises(expected):
            v.normalize()
    else:
        assert (v.normalize() - expected).norm() < 1e-6


def test_vec3_serialize_to_double():
    """Test that a Vec3 object can be serialized to a double."""
    v = Vec3(x=1.0, y=2.0, z=3.0)
    buf = Buffer()
    v.serialize_to_double(buf)

    assert bytes(buf) == struct.pack(">ddd", 1.0, 2.0, 3.0)


def test_vec3_deserialize_from_double():
    """Test that a Vec3 object can be deserialized from a double."""
    buf = Buffer(struct.pack(">ddd", 1.0, 2.0, 3.0))
    v = Vec3.deserialize_double(buf)

    assert type(v) == Vec3
    assert v.x == 1.0
    assert v.y == 2.0
    assert v.z == 3.0
