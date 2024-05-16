from __future__ import annotations

from mcproto.types.uuid import UUID
from tests.helpers import gen_serializable_test

gen_serializable_test(
    context=globals(),
    cls=UUID,
    fields=[("hex", str)],
    test_data=[
        (("12345678-1234-5678-1234-567812345678",), bytes.fromhex("12345678123456781234567812345678")),
        # Too short or too long
        (("12345678-1234-5678-1234-56781234567",), ValueError),
        (("12345678-1234-5678-1234-5678123456789",), ValueError),
        # Not enough data in the buffer (needs 16 bytes)
        (IOError, b""),
        (IOError, b"\x01"),
        (IOError, b"\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e"),
    ],
)
