from __future__ import annotations

from mcproto.types.nbt import ByteNBT, CompoundNBT, IntNBT
from mcproto.types.slot import Slot, SlotData
from tests.helpers import gen_serializable_test

gen_serializable_test(
    context=globals(),
    cls=Slot,
    fields=[("data", "SlotData|None")],
    serialize_deserialize=[
        ((None,), b"\x00"),
        ((SlotData(1, 1, None),), b"\x01\x01\x01\x00"),  # EndNBT() is automatically added
        (
            (SlotData(2, 3, CompoundNBT([IntNBT(4, "int_nbt"), ByteNBT(5, "byte_nbt")])),),
            b"\x01\x02\x03" + CompoundNBT([IntNBT(4, "int_nbt"), ByteNBT(5, "byte_nbt")]).serialize(),
        ),
    ],
)


def test_slot_hash():
    """Test that the slot hash is consistent."""
    s1 = Slot(SlotData(1, 1, None))
    s2 = Slot(SlotData(1, 1, None))

    assert hash(s1) == hash(s2)
    assert s1 == s2

    s1 = Slot(SlotData(1, 1, CompoundNBT([ByteNBT(1, "byte_nbt")])))
    s2 = Slot(SlotData(1, 1, CompoundNBT([ByteNBT(1, "byte_nbt")])))

    assert hash(s1) == hash(s2)
    assert s1 == s2
