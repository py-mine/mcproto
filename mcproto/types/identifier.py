from __future__ import annotations

import re

from attrs import define
from typing_extensions import override

from mcproto.buffer import Buffer
from mcproto.types.abc import MCType
from mcproto.types.nbt import NBTag, NBTagConvertible, StringNBT


@define(init=False)
class Identifier(MCType, NBTagConvertible):
    """A Minecraft identifier."""

    _NAMESPACE_REGEX = re.compile(r"^[a-z0-9\.\-_]+$")
    _PATH_REGEX = re.compile(r"^[a-z0-9\.\-_/]+$")

    namespace: str
    path: str

    @override
    def __init__(self, namespace: str, path: str | None = None):
        """Initialize the Identifier class.

        :param namespace: The namespace of the identifier.
        :param path: The path of the identifier.
        :type path: str, optional

        If the path is not provided, the namespace and path will be extracted from the :attr:`namespace` argument.
        If the namespace is not provided, it will default to "minecraft".

        We use this to initialize the Identifier class instead of attrs because of the extra transformations that we
        need to do, attrs does not support this out of the box.

        """
        if namespace.startswith("#"):
            namespace = namespace[1:]

        if path is None:
            if ":" not in namespace:
                path = namespace
                namespace = "minecraft"
            else:
                namespace, path = namespace.split(":", 1)

        if not self._NAMESPACE_REGEX.match(namespace):
            raise ValueError(f"Invalid namespace: {namespace}")
        if not self._PATH_REGEX.match(path):
            raise ValueError(f"Invalid path: {path}")

        if len(namespace) + len(path) + 1 > 32767:
            raise ValueError("Identifier is too long")

        self.__attrs_init__(namespace=namespace, path=path)  # type: ignore

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
    def __hash__(self) -> int:
        return hash((self.namespace, self.path))

    @override
    def __str__(self) -> str:
        return f"{self.namespace}:{self.path}"

    @override
    def to_nbt(self, name: str = "") -> NBTag:
        return StringNBT(self.__str__(), name=name)
