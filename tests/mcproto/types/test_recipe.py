from tests.helpers import gen_serializable_test
from mcproto.types import (
    Ingredient,
    ShapedRecipe,
    ShapelessRecipe,
    ArmorDyeRecipe,
    SmeltingRecipe,
    StoneCuttingRecipe,
    SmithingTrimRecipe,
    SmithingTransformRecipe,
    Identifier,
    Slot,
)
import struct

gen_serializable_test(
    context=globals(),
    cls=Ingredient,
    fields=[("count", "int"), ("items", "set[Slot]")],
    serialize_deserialize=[
        ((1, {Slot(True, 1, 1, None)}), b"\x01\x01" + Slot(True, 1, 1, None).serialize()),
    ],
    validation_fail=[((1, {Slot(True, 1, 2, None)}), ValueError)],
)


def test_ingredient_set():
    """Test that the set of items gets serialized correctly."""
    ing = Ingredient(1, {Slot(True, 1, 1, None), Slot(True, 2, 1, None)})

    opt1 = b"\x01\x02" + Slot(True, 1, 1, None).serialize() + Slot(True, 2, 1, None).serialize()
    opt2 = b"\x01\x02" + Slot(True, 2, 1, None).serialize() + Slot(True, 1, 1, None).serialize()

    assert ing.serialize() == opt1 or ing.serialize() == opt2  # Set order is not guaranteed


gen_serializable_test(
    context=globals(),
    cls=ShapedRecipe,
    fields=[
        ("recipe_id", Identifier),
        ("group", str),
        ("category", int),
        ("width", int),
        ("height", int),
        ("ingredients", "list[Ingredient]"),
        ("result", Slot),
        ("show_toast", bool),
    ],
    serialize_deserialize=[
        (
            (
                Identifier("minecraft", "test"),
                "test_group",
                1,
                2,
                2,
                [Ingredient(1, {Slot(True, 1, 1, None)})],
                Slot(True, 1, 1, None),
                True,
            ),
            bytes(
                Identifier("minecraft", "test").serialize()
                + b"\x00"  # id
                + b"\x0atest_group\x01\x02\x02\x01"
                + Ingredient(1, {Slot(True, 1, 1, None)}).serialize()
                + Slot(True, 1, 1, None).serialize()
                + b"\x01"
            ),
        ),
    ],
)

gen_serializable_test(
    context=globals(),
    cls=ShapelessRecipe,
    fields=[
        ("recipe_id", Identifier),
        ("group", str),
        ("category", int),
        ("ingredients", "list[Ingredient]"),
        ("result", Slot),
    ],
    serialize_deserialize=[
        (
            (
                Identifier("minecraft", "test"),
                "test_group",
                6,
                [Ingredient(3, {Slot(True, 2, 1, None)})],
                Slot(True, 4, 5, None),
            ),
            bytes(
                Identifier("minecraft", "test").serialize()
                + b"\x01"  # id
                + b"\x0atest_group"
                + b"\x06\x01"  # category + count
                + Ingredient(3, {Slot(True, 2, 1, None)}).serialize()
                + Slot(True, 4, 5, None).serialize()
            ),
        ),
    ],
)

gen_serializable_test(
    context=globals(),
    cls=ArmorDyeRecipe,
    fields=[
        ("recipe_id", Identifier),
        ("category", int),
    ],
    serialize_deserialize=[((Identifier("test"), 1), bytes(Identifier("test").serialize() + b"\x02\01"))],
)


gen_serializable_test(
    context=globals(),
    cls=SmeltingRecipe,
    fields=[
        ("recipe_id", Identifier),
        ("group", str),
        ("category", int),
        ("ingredient", Ingredient),
        ("result", Slot),
        ("experience", float),
        ("cooking_time", int),
    ],
    serialize_deserialize=[
        (
            (
                Identifier("test"),
                "group",
                2,
                Ingredient(3, {Slot(True, 4, 1, None)}),
                Slot(True, 5, 6, None),
                7.0,
                8,
            ),
            bytes(
                Identifier("test").serialize()
                + b"\x0f"  # id
                + b"\x05group\x02"
                + Ingredient(3, {Slot(True, 4, 1, None)}).serialize()
                + Slot(True, 5, 6, None).serialize()
                + struct.pack("!f", 7.0)
                + b"\x08"
            ),
        ),
    ],
)

gen_serializable_test(
    context=globals(),
    cls=StoneCuttingRecipe,
    fields=[
        ("recipe_id", Identifier),
        ("group", str),
        ("ingredient", Ingredient),
        ("result", Slot),
    ],
    serialize_deserialize=[
        (
            (
                Identifier("test"),
                "group",
                Ingredient(3, {Slot(True, 4, 1, None)}),
                Slot(True, 5, 6, None),
            ),
            bytes(
                Identifier("test").serialize()
                + b"\x13"  # id
                + b"\x05group"
                + Ingredient(3, {Slot(True, 4, 1, None)}).serialize()
                + Slot(True, 5, 6, None).serialize()
            ),
        ),
    ],
)


gen_serializable_test(
    context=globals(),
    cls=SmithingTrimRecipe,
    fields=[
        ("recipe_id", Identifier),
        ("template", Ingredient),
        ("base", Ingredient),
        ("addition", Ingredient),
    ],
    serialize_deserialize=[
        (
            (
                Identifier("test"),
                Ingredient(3, {Slot(True, 4, 1, None)}),
                Ingredient(5, {Slot(True, 6, 1, None)}),
                Ingredient(7, {Slot(True, 8, 1, None)}),
            ),
            bytes(
                Identifier("test").serialize()
                + b"\x15"  # id
                + Ingredient(3, {Slot(True, 4, 1, None)}).serialize()
                + Ingredient(5, {Slot(True, 6, 1, None)}).serialize()
                + Ingredient(7, {Slot(True, 8, 1, None)}).serialize()
            ),
        ),
    ],
)


gen_serializable_test(
    context=globals(),
    cls=SmithingTransformRecipe,
    fields=[
        ("recipe_id", Identifier),
        ("template", Ingredient),
        ("base", Ingredient),
        ("addition", Ingredient),
        ("result", Slot),
    ],
    serialize_deserialize=[
        (
            (
                Identifier("test"),
                Ingredient(3, {Slot(True, 4, 1, None)}),
                Ingredient(5, {Slot(True, 6, 1, None)}),
                Ingredient(7, {Slot(True, 8, 1, None)}),
                Slot(True, 9, 10, None),
            ),
            bytes(
                Identifier("test").serialize()
                + b"\x14"  # id
                + Ingredient(3, {Slot(True, 4, 1, None)}).serialize()
                + Ingredient(5, {Slot(True, 6, 1, None)}).serialize()
                + Ingredient(7, {Slot(True, 8, 1, None)}).serialize()
                + Slot(True, 9, 10, None).serialize()
            ),
        ),
    ],
)
