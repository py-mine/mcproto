from __future__ import annotations

import pytest

from mcproto.types.chat import JSONTextComponent, RawTextComponent, RawTextComponentDict, TextComponent
from mcproto.types.nbt import ByteNBT, CompoundNBT, ListNBT, StringNBT
from tests.helpers import gen_serializable_test


@pytest.mark.parametrize(
    ("raw", "expected_dict"),
    [
        (
            {"text": "A Minecraft Server"},
            {"text": "A Minecraft Server"},
        ),
        (
            "A Minecraft Server",
            {"text": "A Minecraft Server"},
        ),
        (
            [{"text": "hello", "bold": True}, {"text": "there"}],
            {"extra": [{"text": "hello", "bold": True}, {"text": "there"}]},
        ),
    ],
)
def test_as_dict(raw: RawTextComponent, expected_dict: RawTextComponentDict):
    """Test converting raw TextComponent input into dict produces expected dict."""
    chat = JSONTextComponent(raw)
    assert chat.as_dict() == expected_dict


@pytest.mark.parametrize(
    ("raw1", "raw2", "expected_result"),
    [
        (
            {"text": "A Minecraft Server"},
            {"text": "A Minecraft Server"},
            True,
        ),
        (
            {"text": "Not a Minecraft Server"},
            {"text": "A Minecraft Server"},
            False,
        ),
    ],
)
def test_equality(raw1: RawTextComponent, raw2: RawTextComponent, expected_result: bool):
    """Test comparing TextComponent instances produces expected equality result."""
    assert (JSONTextComponent(raw1) == JSONTextComponent(raw2)) is expected_result


gen_serializable_test(
    context=globals(),
    cls=JSONTextComponent,
    fields=[("raw", RawTextComponent)],
    serialize_deserialize=[
        (
            ("A Minecraft Server",),
            bytes.fromhex("142241204d696e6563726166742053657276657222"),
        ),
        (
            ({"text": "abc"},),
            bytes.fromhex("0f7b2274657874223a2022616263227d"),
        ),
        (
            ([{"text": "abc"}, {"text": "def"}],),
            bytes.fromhex("225b7b2274657874223a2022616263227d2c207b2274657874223a2022646566227d5d"),
        ),
    ],
    validation_fail=[
        # Wrong type for raw
        ((b"invalid",), TypeError),
        (({"no_extra_or_text": "invalid"},), AttributeError),
        (([{"no_text": "invalid"}, {"text": "Hello"}, {"extra": "World"}],), AttributeError),
        # Expects a list of dicts if raw is a list
        (([[]],), TypeError),
    ],
)

gen_serializable_test(
    context=globals(),
    cls=TextComponent,
    fields=[("raw", RawTextComponent)],
    serialize_deserialize=[
        (({"text": "abc"},), bytes(CompoundNBT([StringNBT("abc", name="text")]).serialize())),
        (
            ([{"text": "abc"}, {"text": "def"}],),
            bytes(
                CompoundNBT(
                    [
                        StringNBT("abc", name="text"),
                        ListNBT([CompoundNBT([StringNBT("def", name="text")])], name="extra"),
                    ]
                ).serialize()
            ),
        ),
        (("A Minecraft Server",), bytes(CompoundNBT([StringNBT("A Minecraft Server", name="text")]).serialize())),
        (
            ([{"text": "abc", "extra": [{"text": "def"}]}, {"text": "ghi"}],),
            bytes(
                CompoundNBT(
                    [
                        StringNBT("abc", name="text"),
                        ListNBT(
                            [
                                CompoundNBT([StringNBT("def", name="text")]),
                                CompoundNBT([StringNBT("ghi", name="text")]),
                            ],
                            name="extra",
                        ),
                    ]
                ).serialize()
            ),
        ),
    ],
    deserialization_fail=[
        # Type shitfuckery
        (bytes(CompoundNBT([CompoundNBT([ByteNBT(0, "Something")], "text")]).serialize()), TypeError),
        (bytes(CompoundNBT([ByteNBT(0, "unknownkey")]).serialize()), KeyError),
        (bytes(CompoundNBT([ListNBT([StringNBT("Expected str")], "text")]).serialize()), TypeError),
        (bytes(CompoundNBT([StringNBT("Wrong type", "extra")]).serialize()), TypeError),
    ],
)
