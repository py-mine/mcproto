from __future__ import annotations

from mcproto.types.nbt import ByteNBT, CompoundNBT, EndNBT, IntNBT, NBTag
from mcproto.types.slot import Slot
from tests.helpers import gen_serializable_test

gen_serializable_test(
    context=globals(),
    cls=Slot,
    fields=[("present", bool), ("item_id", int), ("item_count", int), ("nbt", NBTag)],
    serialize_deserialize=[
        ((False, None, None, None), b"\x00"),
        ((True, 1, 1, None), b"\x01\x01\x01\x00"),  # EndNBT() is automatically added
        ((True, 1, 1, EndNBT()), b"\x01\x01\x01\x00"),
        (
            (True, 2, 3, CompoundNBT([IntNBT(4, "int_nbt"), ByteNBT(5, "byte_nbt")])),
            b"\x01\x02\x03" + CompoundNBT([IntNBT(4, "int_nbt"), ByteNBT(5, "byte_nbt")]).serialize(),
        ),
    ],
    validation_fail=[
        # Present but no item_id
        ((True, None, 1, None), ValueError),
        # Present but no item_count
        ((True, 1, None, None), ValueError),
        # Present but the NBT has the wrong type
        ((True, 1, 1, IntNBT(1, "int_nbt")), TypeError),
        # Not present but item_id is present
        ((False, 1, 1, None), ValueError),
        # Not present but item_count is present
        ((False, None, 1, None), ValueError),
        # Not present but NBT is present
        ((False, None, None, CompoundNBT([])), ValueError),
    ],
)
