from __future__ import annotations

from typing import NamedTuple, final

from attrs import define
from typing_extensions import override

from mcproto.buffer import Buffer
from mcproto.protocol import StructFormat
from mcproto.types.abc import MCType
from mcproto.types.nbt import EndNBT, NBTag

__all__ = ["Slot"]

"""
<https://wiki.vg/Slot_Data>
"""


class SlotData(NamedTuple):
    """Represents the data of a slot in an inventory.

    :param item: The item ID of the item in the slot.
    :type item: int
    :param num: The count of items in the slot.
    :type num: int
    :param nbt: The NBT data of the item in the slot, None if there is no item or no NBT data.
    :type nbt: :class:`~mcproto.types.nbt.NBTag`, optional
    """

    item: int
    num: int
    nbt: NBTag | None = None


@define
@final
class Slot(MCType):
    """Represents a slot in an inventory.

    :param data: The data of the slot.

    .. note:: The optional parameters are present if and only if the slot is present.
    """

    data: SlotData | None

    @override
    def serialize_to(self, buf: Buffer) -> None:
        buf.write_value(StructFormat.BOOL, self.data is not None)
        if self.data is not None:
            buf.write_varint(self.data.item)
            buf.write_value(StructFormat.BYTE, self.data.num)
            if self.data.nbt is None:
                EndNBT().serialize_to(buf)
            else:
                self.data.nbt.serialize_to(buf, with_name=False)
            # In 1.20.2 and later, the NBT is not named, there is only the
            # type (TAG_End or TAG_Compound) and the payload.

    @override
    @classmethod
    def deserialize(cls, buf: Buffer) -> Slot:
        present = buf.read_value(StructFormat.BOOL)
        if not present:
            return cls(None)
        item_id = buf.read_varint()
        item_count = buf.read_value(StructFormat.BYTE)
        nbt = NBTag.deserialize(buf, with_name=False)
        if isinstance(nbt, EndNBT):
            nbt = None
        return cls(SlotData(item_id, item_count, nbt))

    @override
    def __hash__(self) -> int:
        return hash(self.data)
