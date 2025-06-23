from __future__ import annotations

import json
from typing import TypedDict, Union, final

from attrs import define
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
@define
class ChatMessage(MCType):
    """Minecraft chat message representation."""

    raw: RawChatMessage

    __slots__ = ("raw",)

    def as_dict(self) -> RawChatMessageDict:
        """Convert received ``raw`` into a stadard :class:`dict` form."""
        if isinstance(self.raw, list):
            return RawChatMessageDict(extra=self.raw)
        if isinstance(self.raw, str):
            return RawChatMessageDict(text=self.raw)
        if isinstance(self.raw, dict):  # pyright: ignore[reportUnnecessaryIsInstance]
            return self.raw

        raise TypeError(  # pragma: no cover
            f"Found unexpected type ({self.raw.__class__!r}) ({self.raw!r}) in `raw` attribute"
        )

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
    def __hash__(self) -> int:
        return hash(self.raw)

    @override
    def serialize_to(self, buf: Buffer) -> None:
        txt = json.dumps(self.raw)
        buf.write_utf(txt)

    @override
    @classmethod
    def deserialize(cls, buf: Buffer, /) -> Self:
        txt = buf.read_utf()
        dct = json.loads(txt)
        return cls(dct)

    @override
    def validate(self) -> None:
        if not isinstance(self.raw, (dict, list, str)):  # pyright: ignore[reportUnnecessaryIsInstance]
            raise TypeError(f"Expected `raw` to be a dict, list or str, got {self.raw!r} instead")

        if isinstance(self.raw, dict):  # We want to keep it this way for readability
            if "text" not in self.raw and "extra" not in self.raw:
                raise AttributeError("Expected `raw` to have either 'text' or 'extra' key, got neither")

        if isinstance(self.raw, list):
            for elem in self.raw:
                if not isinstance(elem, dict):  # pyright: ignore[reportUnnecessaryIsInstance]
                    raise TypeError(f"Expected `raw` to be a list of dicts, got {elem!r} instead")
                if "text" not in elem and "extra" not in elem:
                    raise AttributeError(
                        "Expected each element in `raw` to have either 'text' or 'extra' key, got neither"
                    )
