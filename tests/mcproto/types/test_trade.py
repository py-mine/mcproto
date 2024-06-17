import struct
from mcproto.types import Trade
from tests.helpers import gen_serializable_test
from mcproto.types import Slot


gen_serializable_test(
    context=globals(),
    cls=Trade,
    fields=[
        ("input_item", Slot),
        ("input_item2", Slot),
        ("output_item", Slot),
        ("trade_disabled", bool),
        ("trade_uses", int),
        ("max_trade_uses", int),
        ("experience", int),
        ("special_price", int),
        ("price_multiplier", float),
        ("demand", int),
    ],
    serialize_deserialize=[
        (
            (
                Slot(True, 6, 64, None),
                Slot(False),
                Slot(True, 1, 1, None),
                False,
                1,
                12,
                16,
                2,
                1.5,
                3,
            ),
            bytes(Slot(True, 6, 64, None).serialize())
            + bytes(Slot(False).serialize())
            + bytes(Slot(True, 1, 1, None).serialize())
            + b"\x00\x01\x0c\x10\x02"
            + struct.pack("!f", 1.5)
            + b"\x03",
        )
    ],
)
