from __future__ import annotations
from attrs import define
from mcproto.types.abc import MCType
from mcproto.types.vec3 import Position
from mcproto.types.nbt import CompoundNBT
from typing import final
from typing_extensions import override, Self
from mcproto.buffer import Buffer
from mcproto.protocol.base_io import StructFormat


@final
@define
class BlockEntity(MCType):
    """Represents a block entity (e.g. a chest, furnace, banner, etc.).

    :param position: The position of the block entity relative to its chunk.
    :type position: Position
    :param block_type: The type of the block entity.
    :type block_type: int
    :param nbt: The NBT data of the block entity.
    :type nbt: CompoundNBT

    .. warning:: The position must be within the chunk.
    .. note :: This class is used in the :class:`~mcproto.packets.play.ChunkData` packet.
    """

    position: Position
    block_type: int
    nbt: CompoundNBT

    @override
    def serialize_to(self, buf: Buffer) -> None:
        x, y, z = int(self.position.x), int(self.position.y), int(self.position.z)

        # Write x and z packed together in a single byte
        buf.write_value(StructFormat.UBYTE, ((x & 15) << 4) | (z & 15))
        buf.write_value(StructFormat.SHORT, y)
        buf.write_varint(self.block_type)
        self.nbt.serialize_to(buf, with_type=False, with_name=False)

    @override
    @classmethod
    def deserialize(cls, buf: Buffer) -> Self:
        packed_xz = buf.read_value(StructFormat.UBYTE)
        x = packed_xz >> 4
        z = packed_xz & 15
        y = buf.read_value(StructFormat.SHORT)
        block_type = buf.read_varint()
        nbt = CompoundNBT.deserialize(  # TODO: Check if with_name=False is correct
            buf, with_name=False, with_type=False
        )
        return cls(Position(x, y, z), block_type, nbt)

    @override
    def validate(self) -> None:
        x, _, z = self.position.x, self.position.y, self.position.z
        if not (0 <= x < 16 and 0 <= z < 16):
            raise ValueError("Position must be within the chunk")
