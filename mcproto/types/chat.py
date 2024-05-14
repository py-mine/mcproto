from __future__ import annotations

import json
from typing import TypedDict, Union, final

from typing_extensions import Self, TypeAlias, override

from mcproto.buffer import Buffer
from mcproto.types.abc import MCType

__all__ = [
    "ChatMessage",
    "RawChatMessage",
    "RawChatMessageDict",
]


class RawChatMessageDict(TypedDict, total=False):
    """Dictionary structure of JSON chat messages when serialized."""

    text: str
    translation: str
    extra: list[RawChatMessageDict]

    color: str
    bold: bool
    strikethrough: bool
    italic: bool
    underlined: bool
    obfuscated: bool


RawChatMessage: TypeAlias = Union[RawChatMessageDict, "list[RawChatMessageDict]", str]


@final
class ChatMessage(MCType):
    """Minecraft chat message representation."""

    __slots__ = ("raw",)

    def __init__(self, raw: RawChatMessage):
        self.raw = raw

    def as_dict(self) -> RawChatMessageDict:
        """Convert received ``raw`` into a stadard :class:`dict` form."""
        if isinstance(self.raw, list):
            return RawChatMessageDict(extra=self.raw)
        if isinstance(self.raw, str):
            return RawChatMessageDict(text=self.raw)
        if isinstance(self.raw, dict):  # pyright: ignore[reportUnnecessaryIsInstance]
            return self.raw
        # pragma: no cover
        raise TypeError(f"Found unexpected type ({self.raw.__class__!r}) ({self.raw!r}) in `raw` attribute")

    @override
    def __eq__(self, other: object) -> bool:
        """Check equality between two chat messages.

        ..warning: This is purely using the `raw` field, which means it's possible that
        a chat message that appears the same, but was representing in a different way
        will fail this equality check.
        """
        if not isinstance(other, ChatMessage):
            return NotImplemented

        return self.raw == other.raw

    @override
    def serialize(self) -> Buffer:
        txt = json.dumps(self.raw)
        buf = Buffer()
        buf.write_utf(txt)
        return buf

    @override
    @classmethod
    def deserialize(cls, buf: Buffer, /) -> Self:
        txt = buf.read_utf()
        dct = json.loads(txt)
        return cls(dct)
