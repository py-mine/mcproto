from __future__ import annotations

from typing import final
from mcproto.buffer import Buffer
from mcproto.types.abc import MCType
from attrs import define

from typing_extensions import override
from mcproto.types.identifier import Identifier


@final
@define
class RegistryTag(MCType):
    """Represents a tag for a registry.

    :param registry: The registry this tag is for.
    :param name: The name of the tag.
    :param values: The values in the tag.
    """

    name: Identifier
    values: list[int]

    @override
    def serialize_to(self, buf: Buffer) -> None:
        self.name.serialize_to(buf)
        buf.write_varint(len(self.values))
        for value in self.values:
            buf.write_varint(value)

    @override
    @classmethod
    def deserialize(cls, buf: Buffer) -> RegistryTag:
        name = Identifier.deserialize(buf)
        values = [buf.read_varint() for _ in range(buf.read_varint())]
        return cls(name, values)

    @override
    def __str__(self) -> str:
        return f"#{self.name}"
