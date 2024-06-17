from __future__ import annotations

from typing import final
from attrs import define

from typing_extensions import override

from mcproto.buffer import Buffer
from mcproto.protocol import StructFormat
from mcproto.types.uuid import UUID
from mcproto.types.abc import MCType
from enum import IntEnum


class ModifierOperation(IntEnum):
    """Represents the operation of a modifier.

    .. note:: The modifier operations are applied in the order :attr:`ADD`, :attr:`ADD_PERCENT`, :attr:`MULTIPLY_TOTAL`
    """

    ADD = 0
    """Add/subtract the amount to the base value."""
    MULTIPLY_BASE = 1
    """Add/subtract a percentage of the base value to the base value."""
    MULTIPLY_TOTAL = 2
    """Multiply the total value by a percentage."""


@final
@define
class ModifierData(MCType):
    """Represents a modifier data in the :class:`mcproto.packets.play.UpdateAttributes` packet.

    https://wiki.vg/Protocol#Update_Attributes

    :param uuid: The UUID of the modifier.
    :type uuid: :class:`mcproto.types.uuid.UUID`
    :param amount: The amount of the modifier.
    :type amount: float
    :param operation: The operation of the modifier.
    :type operation: :class:`ModifierOperation`
    """

    uuid: UUID
    amount: float
    operation: ModifierOperation

    @override
    def serialize_to(self, buf: Buffer) -> None:
        self.uuid.serialize_to(buf)
        buf.write_value(StructFormat.DOUBLE, self.amount)
        buf.write_value(StructFormat.BYTE, self.operation)

    @override
    @classmethod
    def deserialize(cls, buf: Buffer) -> ModifierData:
        uuid = UUID.deserialize(buf)
        amount = buf.read_value(StructFormat.DOUBLE)
        operation = ModifierOperation(buf.read_value(StructFormat.BYTE))
        return cls(uuid=uuid, amount=amount, operation=operation)
