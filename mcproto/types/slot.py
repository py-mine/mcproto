from __future__ import annotations

from typing import cast, final

from typing_extensions import override

from mcproto.buffer import Buffer
from mcproto.protocol import StructFormat
from mcproto.types.nbt import CompoundNBT, EndNBT, NBTag
from mcproto.types.abc import MCType
from attrs import define


__all__ = ["Slot"]

"""
https://wiki.vg/Slot_Data
"""


@define
@final
class Slot(MCType):
    """Represents a slot in an inventory.

    :param present: Whether the slot has an item in it.
    :param item_id: (optional) The item ID of the item in the slot.
    :param item_count: (optional) The count of items in the slot.
    :param nbt: (optional) The NBT data of the item in the slot.

    The optional parameters are present if and only if the slot is present.
    """

    present: bool
    item_id: int | None = None
    item_count: int | None = None
    nbt: NBTag | None = None

    @override
    def serialize_to(self, buf: Buffer) -> None:
        buf.write_value(StructFormat.BOOL, self.present)
        if self.present:
            self.item_id = cast(int, self.item_id)
            self.item_count = cast(int, self.item_count)
            self.nbt = cast(NBTag, self.nbt)
            buf.write_varint(self.item_id)
            buf.write_value(StructFormat.BYTE, self.item_count)
            self.nbt.serialize_to(buf, with_name=False)  # In 1.20.2 and later, the NBT is not named, there is only the
            # type (TAG_End or TAG_Compound) and the payload.

    @override
    @classmethod
    def deserialize(cls, buf: Buffer) -> Slot:
        present = buf.read_value(StructFormat.BOOL)
        if not present:
            return cls(present=False)
        item_id = buf.read_varint()
        item_count = buf.read_value(StructFormat.BYTE)
        nbt = NBTag.deserialize(buf, with_name=False)
        return cls(present=True, item_id=item_id, item_count=item_count, nbt=nbt)

    @override
    def validate(self) -> None:
        # If the slot is present, all the fields must be present.
        if self.present:
            if self.item_id is None:
                raise ValueError("Item ID is missing.")
            if self.item_count is None:
                raise ValueError("Item count is missing.")
            if self.nbt is None:
                self.nbt = EndNBT()
            elif not isinstance(self.nbt, (CompoundNBT, EndNBT)):
                raise TypeError("NBT data associated with a slot must be in a CompoundNBT.")
        else:
            if self.item_id is not None:
                raise ValueError("Item ID must be None if there is no item in the slot.")
            if self.item_count is not None:
                raise ValueError("Item count must be None if there is no item in the slot.")
            if self.nbt is not None and not isinstance(self.nbt, EndNBT):
                raise ValueError("NBT data must be None if there is no item in the slot.")
