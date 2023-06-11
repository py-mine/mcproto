from __future__ import annotations

import pytest

from mcproto.buffer import Buffer
from mcproto.types.uuid import UUID


@pytest.mark.parametrize(
    ("data", "expected_bytes"),
    [
        (
            "12345678-1234-5678-1234-567812345678",
            bytearray.fromhex("12345678123456781234567812345678"),
        ),
    ],
)
def test_serialize(data: str, expected_bytes: list[int]):
    output_bytes = UUID(data).serialize()
    assert output_bytes == expected_bytes


@pytest.mark.parametrize(
    ("input_bytes", "data"),
    [
        (
            bytearray.fromhex("12345678123456781234567812345678"),
            "12345678-1234-5678-1234-567812345678",
        ),
    ],
)
def test_deserialize(input_bytes: list[int], data: str):
    uuid = UUID.deserialize(Buffer(input_bytes))
    assert str(uuid) == data
