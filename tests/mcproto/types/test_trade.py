import struct

from mcproto.types import Slot, SlotData, Trade
from tests.helpers import gen_serializable_test

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
                Slot(SlotData(6, 64)),
                Slot(None),
                Slot(SlotData(1, 1)),
                False,
                1,
                12,
                16,
                2,
                1.5,
                3,
            ),
            bytes(Slot(SlotData(6, 64)).serialize())
            + bytes(Slot(None).serialize())
            + bytes(Slot(SlotData(1, 1)).serialize())
            + b"\x00\x01\x0c\x10\x02"
            + struct.pack("!f", 1.5)
            + b"\x03",
        )
    ],
)
