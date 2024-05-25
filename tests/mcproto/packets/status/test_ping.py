from __future__ import annotations

from mcproto.packets.status.ping import PingPong
from tests.helpers import gen_serializable_test

gen_serializable_test(
    context=globals(),
    cls=PingPong,
    fields=[("payload", int)],
    serialize_deserialize=[
        (
            (2806088,),
            bytes.fromhex("00000000002ad148"),
        ),
        (
            (123456,),
            bytes.fromhex("000000000001e240"),
        ),
    ],
)
