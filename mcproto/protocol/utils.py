from __future__ import annotations

__all__ = ["from_twos_complement", "to_twos_complement"]


def to_twos_complement(number: int, bits: int) -> int:
    """Convert a given ``number`` into twos complement format of given amount of ``bits``.

    :raises ValueError:
        Given ``number`` is out of range, and can't be converted into twos complement format, since
        it wouldn't fit into the given amount of ``bits``.
    """
    value_max = 1 << (bits - 1)
    value_min = value_max * -1
    # With two's complement, we have one more negative number than positive
    # this means we can't be exactly at value_max, but we can be at exactly value_min
    if number >= value_max or number < value_min:
        raise ValueError(f"Can't convert number {number} into {bits}-bit twos complement format - out of range")

    return number + (1 << bits) if number < 0 else number


def from_twos_complement(number: int, bits: int) -> int:
    """Convert a given ``number`` from twos complement format of given amount of ``bits``.

    :raises ValueError:
        Given ``number`` doesn't fit into given amount of ``bits``. This likely means that you're using
        the wrong number, or that the number was converted into twos complement with higher amount of ``bits``.
    """
    value_max = (1 << bits) - 1
    if number < 0 or number > value_max:
        raise ValueError(f"Can't convert number {number} from {bits}-bit twos complement format - out of range")

    if number & (1 << (bits - 1)) != 0:
        number -= 1 << bits

    return number
