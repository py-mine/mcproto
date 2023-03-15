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
        self.raw = raw

    def as_dict(self) -> RawChatMessageDict:
        """Convert received ``raw`` into a stadard :class:`dict` form."""
        if isinstance(self.raw, list):
            return RawChatMessageDict(extra=self.raw)
        elif isinstance(self.raw, str):
            return RawChatMessageDict(text=self.raw)
        elif isinstance(self.raw, dict):
            return self.raw
        else:
            raise TypeError(f"Found unexpected type ({self.raw.__class__!r}) ({self.raw!r}) in `raw` attribute")

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
