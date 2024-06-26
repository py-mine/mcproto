from __future__ import annotations

from typing import final

from attrs import define
from typing_extensions import override

from mcproto.buffer import Buffer
from mcproto.protocol.base_io import StructFormat
from mcproto.types.abc import MCType
from mcproto.types.slot import Slot


@final
@define
class Trade(MCType):
    """Defines a trade in a trade list.

    :param input_item: The item to be traded.
    :type input_item: Slot
    :param input_item2: The second item to be traded.
    :type input_item2: Slot
    :param output_item: The item to be received.
    :type output_item: Slot
    :param trade_disabled: Whether the trade is disabled.
    :type trade_disabled: bool
    :param trade_uses: The number of times the trade has been used.
    :type trade_uses: int
    :param max_trade_uses: The maximum number of times the trade can be used.
    :type max_trade_uses: int
    :param experience: The experience given to the villager when the trade is used.
    :type experience: int
    :param special_price: Price delta for the trade.
    :type special_price: int
    :param price_multiplier: Price multiplier for the trade.
    :type price_multiplier: float
    :param demand: The demand for the trade.
    :type demand: int
    """

    input_item: Slot
    input_item2: Slot
    output_item: Slot
    trade_disabled: bool
    trade_uses: int
    max_trade_uses: int
    experience: int
    special_price: int
    price_multiplier: float
    demand: int

    @override
    def serialize_to(self, buf: Buffer) -> None:
        self.input_item.serialize_to(buf)
        self.input_item2.serialize_to(buf)
        self.output_item.serialize_to(buf)
        buf.write_value(StructFormat.BYTE, int(self.trade_disabled))
        buf.write_varint(self.trade_uses)
        buf.write_varint(self.max_trade_uses)
        buf.write_varint(self.experience)
        buf.write_varint(self.special_price)
        buf.write_value(StructFormat.FLOAT, self.price_multiplier)
        buf.write_varint(self.demand)

    @override
    @classmethod
    def deserialize(cls, buf: Buffer) -> Trade:
        input_item = Slot.deserialize(buf)
        input_item2 = Slot.deserialize(buf)
        output_item = Slot.deserialize(buf)
        trade_disabled = bool(buf.read_value(StructFormat.BYTE))
        trade_uses = buf.read_varint()
        max_trade_uses = buf.read_varint()
        experience = buf.read_varint()
        special_price = buf.read_varint()
        price_multiplier = buf.read_value(StructFormat.FLOAT)
        demand = buf.read_varint()
        return cls(
            input_item=input_item,
            input_item2=input_item2,
            output_item=output_item,
            trade_disabled=trade_disabled,
            trade_uses=trade_uses,
            max_trade_uses=max_trade_uses,
            experience=experience,
            special_price=special_price,
            price_multiplier=price_multiplier,
            demand=demand,
        )
