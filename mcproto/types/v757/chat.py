from __future__ import annotations

import json
from typing import TypeAlias, TypedDict, Union, final

from typing_extensions import Self

from mcproto.buffer import Buffer
from mcproto.types.abc import MCType

__all__ = [
    "ChatMessage",
    "RawChatMessageDict",
    "RawChatMessage",
]


class RawChatMessageDict(TypedDict, total=False):
    text: str
    translation: str
    extra: list[RawChatMessageDict]

    color: str
    bold: bool
    strikethrough: bool
    italic: bool
    underlined: bool
    obfuscated: bool


RawChatMessage: TypeAlias = Union[RawChatMessageDict, list[RawChatMessageDict], str]


@final
class ChatMessage(MCType):
    __slots__ = ("raw",)

    def __init__(self, raw: RawChatMessage):
        if isinstance(raw, list):
            raw = RawChatMessageDict(extra=raw)
        elif isinstance(raw, str):
            raw = RawChatMessageDict(text=raw)

        if isinstance(raw, dict):
            self.raw = raw
        else:
            raise TypeError(f"Expected list, string or dict, got {raw.__class__!r} ({raw!r}), report this!")

    def serialize(self) -> Buffer:
        txt = json.dumps(self.raw)
        buf = Buffer()
        buf.write_utf(txt)
        return buf

    @classmethod
    def deserialize(cls, buf: Buffer, /) -> Self:
        txt = buf.read_utf()
        dct = json.loads(txt)
        return cls(dct)
