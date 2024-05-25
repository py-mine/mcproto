from __future__ import annotations

import pytest

from mcproto.types.chat import ChatMessage, RawChatMessage, RawChatMessageDict
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
def test_as_dict(raw: RawChatMessage, expected_dict: RawChatMessageDict):
    """Test converting raw ChatMessage input into dict produces expected dict."""
    chat = ChatMessage(raw)
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
def test_equality(raw1: RawChatMessage, raw2: RawChatMessage, expected_result: bool):
    """Test comparing ChatMessage instances produces expected equality result."""
    assert (ChatMessage(raw1) == ChatMessage(raw2)) is expected_result


gen_serializable_test(
    context=globals(),
    cls=ChatMessage,
    fields=[("raw", RawChatMessage)],
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
