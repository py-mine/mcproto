from __future__ import annotations

from typing import Any

import pytest

from mcproto.buffer import Buffer
from mcproto.packets.handshaking.handshake import Handshake, NextState


@pytest.mark.parametrize(
    ("kwargs", "expected_bytes"),
    [
        (
            {"protocol_version": 757, "server_address": "mc.aircs.racing", "server_port": 25565, "next_state": 2},
            bytes.fromhex("f5050f6d632e61697263732e726163696e6763dd02"),
        ),
        (
            {"protocol_version": 757, "server_address": "mc.aircs.racing", "server_port": 25565, "next_state": 1},
            bytes.fromhex("f5050f6d632e61697263732e726163696e6763dd01"),
        ),
        (
            {
                "protocol_version": 757,
                "server_address": "hypixel.net",
                "server_port": 25565,
                "next_state": NextState.LOGIN,
            },
            bytes.fromhex("f5050b6879706978656c2e6e657463dd02"),
        ),
        (
            {
                "protocol_version": 757,
                "server_address": "hypixel.net",
                "server_port": 25565,
                "next_state": NextState.STATUS,
            },
            bytes.fromhex("f5050b6879706978656c2e6e657463dd01"),
        ),
    ],
)
def test_serialize(kwargs: dict[str, Any], expected_bytes: list[int]):
    handshake = Handshake(**kwargs)
    assert handshake.serialize().flush() == bytearray(expected_bytes)


@pytest.mark.parametrize(
    ("read_bytes", "expected_out"),
    [
        (
            bytes.fromhex("f5050f6d632e61697263732e726163696e6763dd02"),
            {
                "protocol_version": 757,
                "server_address": "mc.aircs.racing",
                "server_port": 25565,
                "next_state": NextState.LOGIN,
            },
        ),
        (
            bytes.fromhex("f5050f6d632e61697263732e726163696e6763dd01"),
            {
                "protocol_version": 757,
                "server_address": "mc.aircs.racing",
                "server_port": 25565,
                "next_state": NextState.STATUS,
            },
        ),
        (
            bytes.fromhex("f5050b6879706978656c2e6e657463dd02"),
            {
                "protocol_version": 757,
                "server_address": "hypixel.net",
                "server_port": 25565,
                "next_state": NextState.LOGIN,
            },
        ),
        (
            bytes.fromhex("f5050b6879706978656c2e6e657463dd01"),
            {
                "protocol_version": 757,
                "server_address": "hypixel.net",
                "server_port": 25565,
                "next_state": NextState.STATUS,
            },
        ),
    ],
)
def test_deserialize(read_bytes: list[int], expected_out: dict[str, Any]):
    handshake = Handshake.deserialize(Buffer(read_bytes))

    for i, v in expected_out.items():
        assert getattr(handshake, i) == v


@pytest.mark.parametrize(("state"), [3, 4, 5, 6])
def test_invalid_state(state):
    with pytest.raises(ValueError):
        Handshake(protocol_version=757, server_address="localhost", server_port=25565, next_state=state)
