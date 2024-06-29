from mcproto.types.identifier import Identifier
from mcproto.types.nbt import StringNBT
from tests.helpers import gen_serializable_test

gen_serializable_test(
    context=globals(),
    cls=Identifier,
    fields=[("namespace", str), ("path", str)],
    serialize_deserialize=[
        (("minecraft", "stone"), b"\x0fminecraft:stone"),
        (("minecraft", "stone_brick"), b"\x15minecraft:stone_brick"),
        (("minecraft:stone_brick_slab", None), b"\x1aminecraft:stone_brick_slab"),
        (("stone", None), b"\x0fminecraft:stone"),
        (
            ("minecraft.beta", "textures/gui/advancements/backgrounds/end.png"),
            b"\x3cminecraft.beta:textures/gui/advancements/backgrounds/end.png",
        ),
    ],
    validation_fail=[
        (("minecr*ft", "stone_brick_slab_top"), ValueError),  # Invalid namespace
        (("minecraft", "stone_brick_slab_t@p"), ValueError),  # Invalid path
        (("", "something"), ValueError),  # Empty namespace
        (("minecraft", ""), ValueError),  # Empty path
        (("minecraft", "a" * 32767), ValueError),  # Too long
    ],
)


def test__identifier_convert_from_tag():
    """Assert that any # in the namespace is removed."""
    assert Identifier("#minecraft:stone").namespace == "minecraft"
    assert Identifier("#minecraft:stone").path == "stone"
    assert Identifier("#minecraft:stone").serialize() == b"\x0fminecraft:stone"


def test_identifier_hash():
    """Test that the hash function works correctly."""
    assert hash(Identifier("minecraft", "stone")) == hash(Identifier("#stone"))


def test_identifier_str():
    """Test that the string conversion works correctly."""
    assert str(Identifier("minecraft", "stone")) == "minecraft:stone"
    assert str(Identifier("minecraft", "stone_brick")) == "minecraft:stone_brick"
    assert str(Identifier("minecraft:stone_brick_slab", None)) == "minecraft:stone_brick_slab"
    assert str(Identifier("stone")) == "minecraft:stone"


def test_identifier_to_nbt():
    """Test that the identifier can be converted to an NBT tag."""
    assert Identifier("minecraft", "stone").to_nbt() == StringNBT("minecraft:stone")
    assert Identifier("minecraft", "stone_brick").to_nbt("block_held") == StringNBT(
        "minecraft:stone_brick", name="block_held"
    )
