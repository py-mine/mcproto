from __future__ import annotations

import pytest

from mcproto.protocol.utils import from_twos_complement, to_twos_complement

# TODO: Consider adding tests for enforce_range


@pytest.mark.parametrize(
    ("number", "bits", "expected_out"),
    [
        (0, 8, 0),
        (1, 8, 1),
        (10, 8, 10),
        (127, 8, 127),
    ],
)
def test_to_twos_complement_positive(number: int, bits: int, expected_out: int):
    assert to_twos_complement(number, bits) == expected_out


@pytest.mark.parametrize(
    ("number", "bits", "expected_out"),
    [
        (-1, 8, 255),
        (-10, 8, 246),
        (-128, 8, 128),
    ],
)
def test_to_twos_complement_negative(number: int, bits: int, expected_out: int):
    assert to_twos_complement(number, bits) == expected_out


@pytest.mark.parametrize(
    ("number", "bits"),
    [
        (128, 8),
        (-129, 8),
        (32768, 16),
        (-32769, 16),
        (2147483648, 32),
        (-2147483649, 32),
        (9223372036854775808, 64),
        (-9223372036854775809, 64),
    ],
)
def test_to_twos_complement_range(number: int, bits: int):
    with pytest.raises(ValueError, match="out of range"):
        to_twos_complement(number, bits)


@pytest.mark.parametrize(
    ("number", "bits", "expected_out"),
    [
        (0, 8, 0),
        (1, 8, 1),
        (10, 8, 10),
        (127, 8, 127),
    ],
)
def test_from_twos_complement_positive(number: int, bits: int, expected_out: int):
    assert from_twos_complement(number, bits) == expected_out


@pytest.mark.parametrize(
    ("number", "bits", "expected_out"),
    [
        (255, 8, -1),
        (246, 8, -10),
        (128, 8, -128),
    ],
)
def test_from_twos_complement_negative(number: int, bits: int, expected_out: int):
    assert from_twos_complement(number, bits) == expected_out


@pytest.mark.parametrize(
    ("number", "bits"),
    [
        (256, 8),
        (-1, 8),
        (65536, 16),
        (-1, 16),
        (4294967296, 32),
        (-1, 32),
        (18446744073709551616, 64),
        (-1, 64),
    ],
)
def test_from_twos_complement_range(number: int, bits: int):
    with pytest.raises(ValueError, match="out of range"):
        from_twos_complement(number, bits)
