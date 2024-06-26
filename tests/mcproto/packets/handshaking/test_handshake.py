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
    serialize_deserialize=[
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
    ],
    deserialization_fail=[(b"\xf5\x05\x0fmc.aircs.racingc\xdd\x0f", ValueError)],
)
