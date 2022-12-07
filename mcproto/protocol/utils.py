from __future__ import annotations

__all__ = ["to_twos_complement", "from_twos_complement"]


def to_twos_complement(num: int, bits: int) -> int:
    """Convert a given number into twos complement format of given amount of bits."""
    value_max = 1 << (bits - 1)
    value_min = value_max * -1
    # With two's complement, we have one more negative number than positive
    # this means we can't be exactly at value_max, but we can be at exactly value_min
    if num >= value_max or num < value_min:
        raise ValueError(f"Can't convert number {num} into {bits}-bit twos complement format - out of range")

    return num + (1 << bits) if num < 0 else num


def from_twos_complement(num: int, bits: int) -> int:
    """Convert a given number from twos complement format of given amount of bits."""
    value_max = (1 << bits) - 1
    if num < 0 or num > value_max:
        raise ValueError(f"Can't convert number {num} from {bits}-bit twos complement format - out of range")

    if num & (1 << (bits - 1)) != 0:
        num -= 1 << bits

    return num
