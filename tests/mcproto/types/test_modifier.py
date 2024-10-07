import struct

from mcproto.types import ModifierData, ModifierOperation, UUID
from tests.helpers import gen_serializable_test

gen_serializable_test(
    context=globals(),
    cls=ModifierData,
    fields=[
        ("uuid", UUID),
        ("amount", float),
        ("operation", ModifierOperation),
    ],
    serialize_deserialize=[
        (
            (UUID("f70b4a42c9a04ffb92a31390c128a1b2"), 1.5, ModifierOperation.ADD),
            bytes(UUID("f70b4a42c9a04ffb92a31390c128a1b2").serialize() + struct.pack("!d", 1.5) + b"\x00"),
        ),
        (
            (UUID("f70b4a42c9a04ffb92a31390c128a1b2"), 0.5, ModifierOperation.MULTIPLY_TOTAL),
            bytes(UUID("f70b4a42c9a04ffb92a31390c128a1b2").serialize() + struct.pack("!d", 0.5) + b"\x02"),
        ),
    ],
)
