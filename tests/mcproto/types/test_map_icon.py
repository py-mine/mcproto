from mcproto.types import IconType, MapIcon, TextComponent
from tests.helpers import ExcTest, gen_serializable_test

gen_serializable_test(
    context=globals(),
    cls=MapIcon,
    fields=[
        ("icon_type", IconType),
        ("x", int),
        ("z", int),
        ("direction", int),
        ("display_name", TextComponent),
    ],
    serialize_deserialize=[
        (
            (IconType.PLAYER, 0, 0, 0, TextComponent("test")),
            b"\x00\x00\x00\x00\x01" + TextComponent("test").serialize(),
        ),
        ((IconType.WHITE_BANNER, 127, -128, 15, None), b"\x0a\x7f\x80\x0f\x00"),
    ],
    validation_fail=[
        ((IconType.PLAYER, 128, 0, 0, None), ExcTest(ValueError, "<= 127")),
        ((IconType.PLAYER, 0, -129, 0, None), ExcTest(ValueError, ">= -128")),
        ((IconType.PLAYER, 0, 0, 16, None), ExcTest(ValueError, "<= 15")),
    ],
)
