from __future__ import annotations

from typing import final
from mcproto.buffer import Buffer
from mcproto.types.abc import MCType
from attrs import define

from typing_extensions import override
from mcproto.types.chat import TextComponent
from mcproto.protocol.base_io import StructFormat

from enum import IntEnum


class IconType(IntEnum):
    """Represents the type of a map icon."""

    PLAYER = 0
    FRAME = 1
    RED_MARKER = 2
    BLUE_MARKER = 3
    TARGET_X = 4
    TARGET_POINT = 5
    PLAYER_OFF_MAP = 6
    PLAYER_OFF_LIMITS = 7

    MANSION = 8
    MONUMENT = 9

    WHITE_BANNER = 10
    ORANGE_BANNER = 11
    MAGENTA_BANNER = 12
    LIGHT_BLUE_BANNER = 13
    YELLOW_BANNER = 14
    LIME_BANNER = 15
    PINK_BANNER = 16
    GRAY_BANNER = 17
    LIGHT_GRAY_BANNER = 18
    CYAN_BANNER = 19
    PURPLE_BANNER = 20
    BLUE_BANNER = 21
    BROWN_BANNER = 22
    GREEN_BANNER = 23
    RED_BANNER = 24
    BLACK_BANNER = 25

    TREASURE_MARKER = 26


@final
@define
class MapIcon(MCType):
    """Represents a map icon.

    :param type: The type of the icon.
    :type type: IconType
    :param x: The x-coordinate of the icon.
    :type x: int
    :param z: The z-coordinate of the icon.
    :type z: int
    :param direction: The direction of the icon.
    :type direction: int
    :param display_name: The display name of the icon.
    :type display_name: :class:`~mcproto.types.chat.TextComponent`, optional
    """

    icon_type: IconType
    x: int
    z: int
    direction: int
    display_name: TextComponent | None = None

    @override
    def serialize_to(self, buf: Buffer) -> None:
        buf.write_varint(self.icon_type)
        buf.write_value(StructFormat.BYTE, self.x)
        buf.write_value(StructFormat.BYTE, self.z)
        buf.write_value(StructFormat.BYTE, self.direction)
        buf.write_optional(self.display_name, lambda x: x.serialize_to(buf))

    @override
    @classmethod
    def deserialize(cls, buf: Buffer) -> MapIcon:
        icon_type = IconType(buf.read_varint())
        x = buf.read_value(StructFormat.BYTE)
        z = buf.read_value(StructFormat.BYTE)
        direction = buf.read_value(StructFormat.BYTE)
        display_name = buf.read_optional(lambda: TextComponent.deserialize(buf))
        return cls(icon_type, x, z, direction, display_name)

    @override
    def validate(self) -> None:
        if not (-128 <= self.x <= 127):
            raise ValueError("x must be between -128 and 127")
        if not (-128 <= self.z <= 127):
            raise ValueError("z must be between -128 and 127")
        if not (0 <= self.direction <= 15):
            raise ValueError("direction must be between 0 and 15")
