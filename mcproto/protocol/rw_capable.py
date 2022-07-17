from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from mcproto.protocol.base_io import BaseAsyncReader, BaseAsyncWriter, BaseSyncReader, BaseSyncWriter

if TYPE_CHECKING:
    from typing_extensions import Self

__all__ = [
    "ReadCapable",
    "WriteCapable",
    "ReadWriteCapable",
]


class WriteCapable(ABC):
    """Base class providing sync and async writing capabilities."""

    @abstractmethod
    def _serialize(self) -> bytes:
        ...

    def write(self, writer: BaseSyncWriter) -> None:
        data = self._serialize()
        writer.write(data)

    async def async_write(self, writer: BaseAsyncWriter) -> None:
        data = self._serialize()
        await writer.write(data)


class ReadCapable(ABC):
    """Base class providing sync and async reading capabilities."""

    @classmethod
    @abstractmethod
    def read(cls, reader: BaseSyncReader) -> Self:
        ...

    @classmethod
    @abstractmethod
    async def async_read(cls, reader: BaseAsyncReader) -> Self:
        ...


class ReadWriteCapable(ReadCapable, WriteCapable):
    """Base class providing sync and async read+write capabilities."""
