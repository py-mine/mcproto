import pytest

from mcproto.protocol.utils import from_twos_complement, to_twos_complement

# TODO: Consider adding tests for enforce_range


@pytest.mark.parametrize(
    "number,bits,expected_out",
    (
        (0, 8, 0),
        (1, 8, 1),
        (10, 8, 10),
        (127, 8, 127),
    ),
)
def test_to_twos_complement_positive(number: int, bits: int, expected_out: int):
    assert to_twos_complement(number, bits) == expected_out


@pytest.mark.parametrize(
    "number,bits,expected_out",
    (
        (-1, 8, 255),
        (-10, 8, 246),
        (-128, 8, 128),
    ),
)
def test_to_twos_complement_negative(number: int, bits: int, expected_out: int):
    assert to_twos_complement(number, bits) == expected_out


@pytest.mark.parametrize(
    "number,bits,expected_out",
    (
        (0, 8, 0),
        (1, 8, 1),
        (10, 8, 10),
        (127, 8, 127),
    ),
)
def test_from_twos_complement_positive(number: int, bits: int, expected_out: int):
    assert from_twos_complement(number, bits) == expected_out


@pytest.mark.parametrize(
    "number,bits,expected_out",
    (
        (255, 8, -1),
        (246, 8, -10),
        (128, 8, -128),
    ),
)
def test_from_twos_complement_negative(number: int, bits: int, expected_out: int):
    assert from_twos_complement(number, bits) == expected_out
