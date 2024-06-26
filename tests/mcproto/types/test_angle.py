from __future__ import annotations

import pytest

from mcproto.types.angle import Angle
from mcproto.types.vec3 import POS_EAST, POS_NORTH, POS_SOUTH, POS_WEST, POS_ZERO, Position
from tests.helpers import gen_serializable_test

PI = 3.14159265358979323846
EPSILON = 1e-6

gen_serializable_test(
    context=globals(),
    cls=Angle,
    fields=[("angle", int)],
    serialize_deserialize=[
        ((0,), b"\x00"),
        ((256,), b"\x00"),
        ((-1,), b"\xff"),
        ((-256,), b"\x00"),
        ((2,), b"\x02"),
        ((-2,), b"\xfe"),
    ],
)


@pytest.mark.parametrize(
    ("angle", "base", "distance", "expected"),
    [
        (Angle(0), POS_ZERO, 1, POS_SOUTH),
        (Angle(64), POS_ZERO, 1, POS_WEST),
        (Angle(128), POS_ZERO, 1, POS_NORTH),
        (Angle(192), POS_ZERO, 1, POS_EAST),
    ],
)
def test_in_direction(angle: Angle, base: Position, distance: int, expected: Position):
    """Test that the in_direction method moves the base position in the correct direction."""
    assert (angle.in_direction(base, distance) - expected).norm() < EPSILON


@pytest.mark.parametrize(
    ("base2", "degrees"),
    [
        (0, 0),
        (64, 90),
        (128, 180),
        (192, 270),
    ],
)
def test_degrees(base2: int, degrees: int):
    """Test that the from_degrees and to_degrees methods work correctly."""
    assert Angle.from_degrees(degrees) == Angle(base2)
    assert Angle(base2).to_degrees() == degrees


@pytest.mark.parametrize(
    ("rad", "angle"),
    [
        (0, 0),
        (PI / 2, 64),
        (PI, 128),
        (3 * PI / 2, 192),
    ],
)
def test_radians(rad: float, angle: int):
    """Test that the from_radians and to_radians methods work correctly."""
    assert Angle.from_radians(rad) == Angle(angle)
    assert abs(Angle(angle).to_radians() - rad) < EPSILON
