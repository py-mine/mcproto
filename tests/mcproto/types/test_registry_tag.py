from tests.helpers import gen_serializable_test
from mcproto.types import RegistryTag, Identifier

gen_serializable_test(
    context=globals(),
    cls=RegistryTag,
    fields=[
        ("name", Identifier),
        ("values", "list[int]"),
    ],
    serialize_deserialize=[
        ((Identifier("wool"), [1, 2, 3]), bytes(Identifier("wool").serialize() + b"\x03\x01\x02\x03")),
        ((Identifier("block"), [1, 2, 3, 4]), bytes(Identifier("block").serialize() + b"\x04\x01\x02\x03\x04")),
    ],
)


def test_registry_tag_str():
    """Test that registry tags can be printed as strings correctly."""
    assert str(RegistryTag(Identifier("stone"), [1, 2, 3])) == "#minecraft:stone"
