from mcproto.types.entity import PandaEM
from mcproto.buffer import Buffer


import pytest
from mcproto.types.entity.metadata import proxy, entry, EntityMetadataCreator, EntityMetadata
from mcproto.types.entity.metadata_types import ByteEME, Masked


def test_panda():
    """Test the Panda entity (it has a lot of inherited fields, so it's a good test case)."""
    panda = PandaEM()

    assert panda.serialize() == b"\xff"  # No metadata

    panda.active_hand = 0
    panda.is_hand_active = True
    panda.is_riptide_spin_attack = True
    # Index 8, Type 0 (byte), Value 0b00000101
    assert panda.serialize() == b"\x08\x00\x05\xff"
    # 0bxx1 hand active
    # 0bx0x main hand active (1 for offhand)
    # 0b1xx riptide spin attack

    panda.is_sneezing = True
    # Index 8, Type 0 (byte), Value 0b00000101, Index 22, Type 0 (byte), Value 2
    assert panda.serialize() == b"\x08\x00\x05\x16\x00\x02\xff"

    panda.active_hand = 0
    panda.is_hand_active = False
    panda.is_riptide_spin_attack = False
    panda.eat_timer = -1  # VarInt 0xff 0xff 0xff 0xff 0x0f
    # Index 22, Type 0 (byte), Value 2, Index 19, Type 1 (VarInt), Value -1
    assert panda.serialize() == b"\x13\x01\xff\xff\xff\xff\x0f\x16\x00\x02\xff"

    buf = Buffer(b"\x13\x01\x02\x16\x00\x02\x08\x00\x07\xff")
    panda2 = PandaEM.deserialize(buf)
    assert panda2.active_hand == 1
    assert panda2.is_hand_active
    assert panda2.is_riptide_spin_attack
    assert panda2.eat_timer == 2
    assert panda2.is_sneezing
    assert not panda2.is_sitting


def test_kwargs():
    """Test kwargs for EnitityMetadata."""
    panda = PandaEM(custom_name="test", is_custom_name_visible=True)
    assert panda.custom_name == "test"
    assert panda.is_custom_name_visible


def test_class_error():
    """Test errors for EntityMetadataCreator."""
    with pytest.raises(TypeError):
        proxy("test", Masked, mask=0x1)  # wrong type

    with pytest.raises(TypeError):
        proxy(object, Masked, mask=0x1)  # wrong type

    with pytest.raises(ValueError):

        class Test(metaclass=EntityMetadataCreator):  # type: ignore
            test: int

    with pytest.raises(ValueError):

        class Test(metaclass=EntityMetadataCreator):  # type: ignore # noqa: F811
            test: int = 0

    with pytest.raises(ValueError):
        EntityMetadata(1, 1)  # type: ignore

    with pytest.raises(ValueError):

        class Test(metaclass=EntityMetadataCreator):  # noqa: F811
            test: int = proxy(entry(ByteEME, 1), Masked, mask=0x1)

    buf = Buffer(b"\x00\x02\x00")  # Wrong metadata type
    with pytest.raises(TypeError):
        ByteEME.deserialize(buf)

    EntityMetadata()

    buf = Buffer(b"\x00\xff\x00")  # Invalid metadata type
    with pytest.raises(TypeError):
        EntityMetadata.deserialize(buf)

    with pytest.raises(ValueError):
        EntityMetadata(keyword="test")
