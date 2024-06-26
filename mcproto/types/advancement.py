from __future__ import annotations

from enum import IntEnum
from typing import final

from attrs import define
from typing_extensions import override

from mcproto.buffer import Buffer
from mcproto.protocol import StructFormat
from mcproto.types.abc import MCType
from mcproto.types.chat import TextComponent
from mcproto.types.identifier import Identifier
from mcproto.types.slot import Slot


@final
@define
class Advancement(MCType):
    """Represents an advancement in the game.

    Non-standard type, see: `<https://wiki.vg/Protocol#Update_Advancements>`

    :param parent: The parent advancement.
    :type parent: :class:`~mcproto.types.identifier.Identifier`, optional
    :param display: The display information.
    :type display: :class:`AdvancementDisplay`, optional
    :param requirements: The criteria for this advancement.
    :type requirements: list[list[str]]
    :param telemetry: Whether to send telemetry data.
    :type telemetry: bool
    """

    parent: Identifier | None
    display: AdvancementDisplay | None
    requirements: list[list[str]]
    telemetry: bool

    @override
    def serialize_to(self, buf: Buffer) -> None:
        buf.write_optional(self.parent, lambda x: x.serialize_to(buf))
        buf.write_optional(self.display, lambda x: x.serialize_to(buf))
        buf.write_varint(len(self.requirements))
        for requirement in self.requirements:
            buf.write_varint(len(requirement))
            for criterion in requirement:
                buf.write_utf(criterion)
        buf.write_value(StructFormat.BOOL, self.telemetry)

    @override
    @classmethod
    def deserialize(cls, buf: Buffer) -> Advancement:
        parent = buf.read_optional(lambda: Identifier.deserialize(buf))
        display = buf.read_optional(lambda: AdvancementDisplay.deserialize(buf))
        requirements = [[buf.read_utf() for _ in range(buf.read_varint())] for _ in range(buf.read_varint())]
        telemetry = buf.read_value(StructFormat.BOOL)
        return cls(parent=parent, display=display, requirements=requirements, telemetry=telemetry)


class AdvancementFrame(IntEnum):
    """Represents the shape of the frame of an advancement in the GUI."""

    TASK = 0
    CHALLENGE = 1
    GOAL = 2


@final
@define
class AdvancementDisplay(MCType):
    """Describes how an advancement should look.

    :param title: The title of the advancement.
    :type title: :class:`~mcproto.types.chat.TextComponent`
    :param description: The description of the advancement.
    :type description: :class:`~mcproto.types.chat.TextComponent`
    :param icon: The icon of the advancement.
    :type icon: :class:`~mcproto.types.slot.Slot`
    :param frame: The frame of the advancement.
    :type frame: :class:`AdvancementFrame`
    :param background: The background texture of the advancement.
    :type background: :class:`~mcproto.types.identifier.Identifier`, optional
    :param show_toast: Whether to show a toast notification.
    :type show_toast: bool
    :param hidden: Whether the advancement is hidden.
    :type hidden: bool
    :param x: The x-coordinate of the advancement (in the GUI).
    :type x: float
    :param y: The y-coordinate of the advancement (in the GUI).
    :type y: float
    """

    title: TextComponent
    description: TextComponent
    icon: Slot
    frame: AdvancementFrame
    background: Identifier | None
    show_toast: bool
    hidden: bool
    x: float
    y: float

    @override
    def serialize_to(self, buf: Buffer) -> None:
        self.title.serialize_to(buf)
        self.description.serialize_to(buf)
        self.icon.serialize_to(buf)
        buf.write_varint(self.frame.value)

        flags = (self.background is not None) << 0 | self.show_toast << 1 | self.hidden << 2
        buf.write_value(StructFormat.BYTE, flags)
        if self.background is not None:
            self.background.serialize_to(buf)
        buf.write_value(StructFormat.FLOAT, self.x)
        buf.write_value(StructFormat.FLOAT, self.y)

    @override
    @classmethod
    def deserialize(cls, buf: Buffer) -> AdvancementDisplay:
        title = TextComponent.deserialize(buf)
        description = TextComponent.deserialize(buf)
        icon = Slot.deserialize(buf)
        frame = AdvancementFrame(buf.read_varint())
        flags = buf.read_value(StructFormat.BYTE)
        background = Identifier.deserialize(buf) if flags & 0x1 else None
        show_toast = bool(flags & 0x2)
        hidden = bool(flags & 0x4)
        x = buf.read_value(StructFormat.FLOAT)
        y = buf.read_value(StructFormat.FLOAT)
        return cls(
            title=title,
            description=description,
            icon=icon,
            frame=frame,
            background=background,
            show_toast=show_toast,
            hidden=hidden,
            x=x,
            y=y,
        )


@final
@define
class AdvancementProgress(MCType):
    """Represents the progress of an advancement.

    :param criteria: The criteria for this advancement.
    :type criteria: dict[:class:`~mcproto.types.identifier.Identifier`, :class:`AdvancementCriterion`]
    """

    criteria: dict[Identifier, AdvancementCriterion]

    @override
    def serialize_to(self, buf: Buffer) -> None:
        buf.write_varint(len(self.criteria))
        for identifier, criterion in self.criteria.items():
            identifier.serialize_to(buf)
            criterion.serialize_to(buf)

    @override
    @classmethod
    def deserialize(cls, buf: Buffer) -> AdvancementProgress:
        criteria = {
            Identifier.deserialize(buf): AdvancementCriterion.deserialize(buf) for _ in range(buf.read_varint())
        }
        return cls(criteria=criteria)


@final
@define
class AdvancementCriterion(MCType):
    """Represents a criterion for an advancement.

    :param date: The date the criterion was achieved. (As returned by Date.getTime() in Java), None if not achieved.
    :type date: int, optional
    """

    date: int | None = None

    @override
    def serialize_to(self, buf: Buffer) -> None:
        buf.write_optional(self.date, lambda x: buf.write_value(StructFormat.LONGLONG, x))

    @override
    @classmethod
    def deserialize(cls, buf: Buffer) -> AdvancementCriterion:
        date = buf.read_optional(lambda: buf.read_value(StructFormat.LONGLONG))
        return cls(date=date)

    @property
    def achieved(self) -> bool:
        """Whether the criterion was achieved."""
        return self.date is not None
