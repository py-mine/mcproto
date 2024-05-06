from __future__ import annotations

import re
from typing_extensions import override

from mcproto.buffer import Buffer
from mcproto.types.abc import MCType
from attrs import define


@define
class Identifier(MCType):
    """A Minecraft identifier.

    :param namespace: The namespace of the identifier.
    :param path: The path of the identifier.
    """

    namespace: str
    path: str

    @override
    def serialize_to(self, buf: Buffer) -> None:
        data = f"{self.namespace}:{self.path}"
        buf.write_utf(data)

    @override
    @classmethod
    def deserialize(cls, buf: Buffer) -> Identifier:
        data = buf.read_utf()
        namespace, path = data.split(":", 1)
        return cls(namespace, path)

    @override
    def validate(self) -> None:
        if len(self.namespace) == 0:
            raise ValueError("Namespace cannot be empty.")

        if len(self.path) == 0:
            raise ValueError("Path cannot be empty.")

        if len(self.namespace) + len(self.path) + 1 > 32767:
            raise ValueError("Identifier is too long.")

        namespace_regex = r"^[a-z0-9-_]+$"
        path_regex = r"^[a-z0-9-_/]+$"

        if not re.match(namespace_regex, self.namespace):
            raise ValueError(f"Namespace must match regex {namespace_regex}, got {self.namespace!r}")

        if not re.match(path_regex, self.path):
            raise ValueError(f"Path must match regex {path_regex}, got {self.path!r}")
