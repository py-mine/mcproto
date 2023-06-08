from __future__ import annotations

from typing import Any

import pytest

from mcproto.buffer import Buffer
from mcproto.packets.status.ping import PingPong


@pytest.mark.parametrize(
    ("kwargs", "expected_bytes"),
    [
        ({"payload": 2806088}, bytes.fromhex("00000000002ad148")),
        ({"payload": 123456}, bytes.fromhex("000000000001e240")),
    ],
)
def test_serialize(kwargs: dict[str, Any], expected_bytes: list[int]):
    ping = PingPong(**kwargs)
    assert ping.serialize().flush() == bytearray(expected_bytes)


@pytest.mark.parametrize(
    ("read_bytes", "expected_out"),
    [
        (bytes.fromhex("00000000002ad148"), {"payload": 2806088}),
        (bytes.fromhex("000000000001e240"), {"payload": 123456}),
    ],
)
def test_deserialize(read_bytes: list[int], expected_out: dict[str, Any]):
    ping = PingPong.deserialize(Buffer(read_bytes))

    for i, v in expected_out.items():
        assert getattr(ping, i) == v
