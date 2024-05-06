from __future__ import annotations
import struct
from typing import cast
import pytest
import math
from mcproto.types.quaternion import Quaternion
from tests.helpers import gen_serializable_test

gen_serializable_test(
    context=globals(),
    cls=Quaternion,
    fields=[("x", float), ("y", float), ("z", float), ("w", float)],
    serialize_deserialize=[
        ((0.0, 0.0, 0.0, 0.0), struct.pack(">ffff", 0.0, 0.0, 0.0, 0.0)),
        ((-1.0, -1.0, -1.0, -1.0), struct.pack(">ffff", -1.0, -1.0, -1.0, -1.0)),
        ((1.0, 2.0, 3.0, 4.0), struct.pack(">ffff", 1.0, 2.0, 3.0, 4.0)),
        ((1.5, 2.5, 3.5, 4.5), struct.pack(">ffff", 1.5, 2.5, 3.5, 4.5)),
    ],
    validation_fail=[
        # Invalid values
        ((1.0, 2.0, "3.0", 4.0), TypeError),
        ((float("nan"), 2.0, 3.0, 4.0), ValueError),
        ((1.0, float("inf"), 3.0, 4.0), ValueError),
        ((1.0, 2.0, -float("inf"), 4.0), ValueError),
    ],
)


def test_quaternion_addition():
    """Test that two Quaternion objects can be added together (resulting in a new Quaternion object)."""
    v1 = Quaternion(x=1.0, y=2.0, z=3.0, w=4.0)
    v2 = Quaternion(x=4.5, y=5.25, z=6.125, w=7.0625)
    v3 = v1 + v2
    assert type(v3) == Quaternion
    assert v3.x == 5.5
    assert v3.y == 7.25
    assert v3.z == 9.125
    assert v3.w == 11.0625


def test_quaternion_subtraction():
    """Test that two Quaternion objects can be subtracted (resulting in a new Quaternion object)."""
    v1 = Quaternion(x=1.0, y=2.0, z=3.0, w=4.0)
    v2 = Quaternion(x=4.5, y=5.25, z=6.125, w=7.0625)
    v3 = v2 - v1
    assert type(v3) == Quaternion
    assert v3.x == 3.5
    assert v3.y == 3.25
    assert v3.z == 3.125
    assert v3.w == 3.0625


def test_quaternion_negative():
    """Test that a Quaternion object can be negated."""
    v1 = Quaternion(x=1.0, y=2.5, z=3.0, w=4.5)
    v2 = -v1
    assert type(v2) == Quaternion
    assert v2.x == -1.0
    assert v2.y == -2.5
    assert v2.z == -3.0
    assert v2.w == -4.5


def test_quaternion_multiplication_int():
    """Test that a Quaternion object can be multiplied by an integer."""
    v1 = Quaternion(x=1.0, y=2.25, z=3.0, w=4.5)
    v2 = v1 * 2
    assert v2.x == 2.0
    assert v2.y == 4.5
    assert v2.z == 6.0
    assert v2.w == 9.0


def test_quaternion_multiplication_float():
    """Test that a Quaternion object can be multiplied by a float."""
    v1 = Quaternion(x=2.0, y=4.5, z=6.0, w=9.0)
    v2 = v1 * 1.5
    assert type(v2) == Quaternion
    assert v2.x == 3.0
    assert v2.y == 6.75
    assert v2.z == 9.0
    assert v2.w == 13.5


def test_quaternion_norm_squared():
    """Test that the squared norm of a Quaternion object can be calculated."""
    v = Quaternion(x=3.0, y=4.0, z=5.0, w=6.0)
    assert v.norm_squared() == 86.0


def test_quaternion_norm():
    """Test that the norm of a Quaternion object can be calculated."""
    v = Quaternion(x=3.0, y=4.0, z=5.0, w=6.0)
    assert (v.norm() - 86.0**0.5) < 1e-6


@pytest.mark.parametrize(
    ("x", "y", "z", "w", "expected"),
    [
        (0, 0, 0, 0, ZeroDivisionError),
        (1, 0, 0, 0, Quaternion(x=1, y=0, z=0, w=0)),
        (0, 1, 0, 0, Quaternion(x=0, y=1, z=0, w=0)),
        (0, 0, 1, 0, Quaternion(x=0, y=0, z=1, w=0)),
        (0, 0, 0, 1, Quaternion(x=0, y=0, z=0, w=1)),
        (1, 1, 1, 1, Quaternion(x=1, y=1, z=1, w=1) / math.sqrt(4)),
        (-1, -1, -1, -1, Quaternion(x=-1, y=-1, z=-1, w=-1) / math.sqrt(4)),
    ],
)
def test_quaternion_normalize(x: float, y: float, z: float, w: float, expected: Quaternion | type):
    """Test that a Quaternion object can be normalized."""
    v = Quaternion(x=x, y=y, z=z, w=w)
    if isinstance(expected, type):
        expected = cast("type[Exception]", expected)
        with pytest.raises(expected):
            v.normalize()
    else:
        assert (v.normalize() - expected).norm() < 1e-6


def test_quaternion_tuple():
    """Test that a Quaternion object can be converted to a tuple."""
    v = Quaternion(x=1.0, y=2.0, z=3.0, w=4.0)
    assert v.to_tuple() == (1.0, 2.0, 3.0, 4.0)
