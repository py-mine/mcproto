from mcproto.types.identifier import Identifier
from tests.helpers import gen_serializable_test


gen_serializable_test(
    context=globals(),
    cls=Identifier,
    fields=[("namespace", str), ("path", str)],
    serialize_deserialize=[
        (("minecraft", "stone"), b"\x0fminecraft:stone"),
        (("minecraft", "stone_brick"), b"\x15minecraft:stone_brick"),
        (("minecraft", "stone_brick_slab"), b"\x1aminecraft:stone_brick_slab"),
    ],
    validation_fail=[
        (("minecr*ft", "stone_brick_slab_top"), ValueError),  # Invalid namespace
        (("minecraft", "stone_brick_slab_t@p"), ValueError),  # Invalid path
        (("", "something"), ValueError),  # Empty namespace
        (("minecraft", ""), ValueError),  # Empty path
        (("minecraft", "a" * 32767), ValueError),  # Too long
    ],
)
