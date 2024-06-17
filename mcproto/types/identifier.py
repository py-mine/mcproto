from __future__ import annotations

import re
from typing_extensions import override

from mcproto.buffer import Buffer
from mcproto.types.abc import MCType
from attrs import define
from mcproto.types.nbt import NBTag, StringNBT, NBTagConvertible


@define
class Identifier(MCType, NBTagConvertible):
    """A Minecraft identifier.

    :param namespace: The namespace of the identifier.
    :param path: The path of the identifier.
    :type path: str, optional

    If the path is not provided, the namespace and path will be extracted from the :arg:`namespace` argument.
    If the namespace is not provided, it will default to "minecraft".
    """

    namespace: str
    path: str

    @override
    def __init__(self, namespace: str, path: str | None = None) -> None:
        if namespace.startswith("#"):
            namespace = namespace[1:]

        if path is None:
            if ":" not in namespace:
                namespace, path = "minecraft", namespace  # Default namespace
            else:
                namespace, path = namespace.split(":", 1)

        self.__attrs_init__(namespace=namespace, path=path)  # type: ignore # @define makes this a dataclass

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

        namespace_regex = r"^[a-z0-9\.\-_]+$"
        path_regex = r"^[a-z0-9\.\-_/]+$"

        if not re.match(namespace_regex, self.namespace):
            raise ValueError(f"Namespace must match regex {namespace_regex}, got {self.namespace!r}")

        if not re.match(path_regex, self.path):
            raise ValueError(f"Path must match regex {path_regex}, got {self.path!r}")

    @override
    def __hash__(self) -> int:
        return hash((self.namespace, self.path))

    @override
    def __str__(self) -> str:
        return f"{self.namespace}:{self.path}"

    @override
    def to_nbt(self, name: str = "") -> NBTag:
        return StringNBT(self.__str__(), name=name)
