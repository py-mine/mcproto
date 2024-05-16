from __future__ import annotations

from mcproto.packets.handshaking.handshake import Handshake, NextState
from tests.helpers import gen_serializable_test

gen_serializable_test(
    context=globals(),
    cls=Handshake,
    fields=[
        ("protocol_version", int),
        ("server_address", str),
        ("server_port", int),
        ("next_state", NextState),
    ],
    test_data=[
        (
            (757, "mc.aircs.racing", 25565, NextState.LOGIN),
            bytes.fromhex("f5050f6d632e61697263732e726163696e6763dd02"),
        ),
        (
            (757, "mc.aircs.racing", 25565, NextState.STATUS),
            bytes.fromhex("f5050f6d632e61697263732e726163696e6763dd01"),
        ),
        (
            (757, "hypixel.net", 25565, NextState.LOGIN),
            bytes.fromhex("f5050b6879706978656c2e6e657463dd02"),
        ),
        (
            (757, "hypixel.net", 25565, NextState.STATUS),
            bytes.fromhex("f5050b6879706978656c2e6e657463dd01"),
        ),
        # Invalid next state
        ((757, "localhost", 25565, 3), ValueError),
        ((757, "localhost", 25565, 4), ValueError),
        ((757, "localhost", 25565, 5), ValueError),
        ((757, "localhost", 25565, 6), ValueError),
    ],
)
