from tests.helpers import gen_serializable_test
from mcproto.types import BlockEntity, Position, CompoundNBT
from mcproto.types.nbt import ByteNBT

gen_serializable_test(
    context=globals(),
    cls=BlockEntity,
    fields=[
        ("position", Position),
        ("block_type", int),
        ("nbt", CompoundNBT),
    ],
    serialize_deserialize=[
        (
            (Position(2, 65, 8), 1, CompoundNBT([ByteNBT(1, "test")])),
            b"\x28\x00\x41\x01" + CompoundNBT([ByteNBT(1, "test")]).serialize(with_type=False),
        ),
    ],
    validation_fail=[
        ((Position(0, 0, 16), 1, CompoundNBT([ByteNBT(1, "test")])), ValueError),
        ((Position(16, 0, 0), 1, CompoundNBT([ByteNBT(1, "test")])), ValueError),
        ((Position(-1, 0, 0), 1, CompoundNBT([ByteNBT(1, "test")])), ValueError),
        ((Position(0, 0, -1), 1, CompoundNBT([ByteNBT(1, "test")])), ValueError),
    ],
)
