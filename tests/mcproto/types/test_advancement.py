import struct

from mcproto.types import (
    Advancement,
    AdvancementCriterion,
    AdvancementDisplay,
    AdvancementFrame,
    AdvancementProgress,
    Identifier,
    Slot,
    SlotData,
    TextComponent,
)
from tests.mcproto.utils.test_serializable import gen_serializable_test

gen_serializable_test(
    context=globals(),
    cls=AdvancementDisplay,
    fields=[
        ("title", TextComponent),
        ("description", TextComponent),
        ("icon", Slot),
        ("frame", AdvancementFrame),
        ("background", "Identifier|None"),
        ("show_toast", bool),
        ("hidden", bool),
        ("x", float),
        ("y", float),
    ],
    serialize_deserialize=[
        (
            (
                TextComponent("The End?"),
                TextComponent("Go there"),
                Slot(SlotData(2, 1)),
                AdvancementFrame.CHALLENGE,
                Identifier(namespace="minecraft", path="textures/gui/advancements/backgrounds/end.png"),
                True,
                False,
                0.5,
                0.5,
            ),
            bytes(
                TextComponent("The End?").serialize()
                + TextComponent("Go there").serialize()
                + Slot(SlotData(2, 1)).serialize()
                + b"\x01"  # frame
                + b"\x03"  # 0b011
                + Identifier(namespace="minecraft", path="textures/gui/advancements/backgrounds/end.png").serialize()
                + struct.pack("!ff", 0.5, 0.5)
            ),
        ),
        (
            (
                TextComponent("The End?"),
                TextComponent("Go there"),
                Slot(SlotData(2, 1)),
                AdvancementFrame.TASK,
                None,
                False,
                True,
                0.5,
                0.5,
            ),
            bytes(
                TextComponent("The End?").serialize()
                + TextComponent("Go there").serialize()
                + Slot(SlotData(2, 1)).serialize()
                + b"\x00"  # frame
                + b"\x04"  # 0b100
                + struct.pack("!ff", 0.5, 0.5)
            ),
        ),
    ],
)


gen_serializable_test(
    context=globals(),
    cls=Advancement,
    fields=[
        ("parent", "Identifier|None"),
        ("display", AdvancementDisplay),
        ("requirements", "list[list[str]]"),
        ("telemetry", bool),
    ],
    serialize_deserialize=[
        (
            (
                Identifier("minecraft", "stone"),
                AdvancementDisplay(
                    TextComponent("The End?"),
                    TextComponent("Go there"),
                    Slot(SlotData(2, 1)),
                    AdvancementFrame.GOAL,
                    Identifier(namespace="minecraft", path="textures/gui/advancements/backgrounds/end.png"),
                    True,
                    False,
                    0.5,
                    0.5,
                ),
                [["minecraft:stone"]],
                True,
            ),
            bytes(
                b"\x01"  # Present
                + Identifier("minecraft", "stone").serialize()
                + b"\x01"  # Present
                + AdvancementDisplay(
                    TextComponent("The End?"),
                    TextComponent("Go there"),
                    Slot(SlotData(2, 1)),
                    AdvancementFrame.GOAL,
                    Identifier(namespace="minecraft", path="textures/gui/advancements/backgrounds/end.png"),
                    True,
                    False,
                    0.5,
                    0.5,
                ).serialize()
                + b"\x01"  # requirements length
                + b"\x01"  # requirement 1 length
                + b"\x0fminecraft:stone"  # requirement 1
                + b"\x01"  # telemetry
            ),
        ),
        (
            (
                None,
                None,
                [["minecraft:stone", "minecraft:stone_brick"], ["minecraft:stone"]],
                False,
            ),
            bytes(
                b"\x00"  # Absent  # noqa: ISC003
                + b"\x00"  # Absent
                + b"\x02"  # requirements length
                + b"\x02"  # requirement 1 length
                + b"\x0fminecraft:stone"  # requirement 1
                + b"\x15minecraft:stone_brick"  # requirement 2
                + b"\x01"  # requirement 2 length
                + b"\x0fminecraft:stone"  # requirement 2
                + b"\x00"  # telemetry
            ),
        ),
    ],
)


gen_serializable_test(
    context=globals(),
    cls=AdvancementProgress,
    fields=[
        ("criteria", "dict[Identifier, AdvancementCriterion]"),
    ],
    serialize_deserialize=[
        (
            (
                {
                    Identifier("minecraft", "stone"): AdvancementCriterion(None),
                    Identifier("minecraft", "stone_brick"): AdvancementCriterion(1081165320000),
                },
            ),
            bytes(
                b"\x02"  # criteria length
                + Identifier("minecraft", "stone").serialize()
                + AdvancementCriterion(None).serialize()
                + b"\x15minecraft:stone_brick"  # identifier 2
                + AdvancementCriterion(1081165320000).serialize()
            ),
        ),
        (
            ({},),
            b"\x00",  # criteria length
        ),
    ],
)

gen_serializable_test(
    context=globals(),
    cls=AdvancementCriterion,
    fields=[
        ("date", "int|None"),
    ],
    serialize_deserialize=[
        ((None,), b"\x00"),  # Absent
        ((1081165320000,), b"\x01" + struct.pack("!q", 1081165320000)),  # Present
    ],
)


def test_criterion_achieved():
    """Test that the achieved property works correctly."""
    assert AdvancementCriterion(None).achieved is False
    assert AdvancementCriterion(1081165320000).achieved is True
