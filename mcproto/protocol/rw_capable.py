from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable, Sequence
from dataclasses import dataclass
from functools import partial
from typing import ClassVar, Generic, TYPE_CHECKING, TypeVar

from mcproto.protocol.base_io import BaseAsyncReader, BaseAsyncWriter, BaseSyncReader, BaseSyncWriter

if TYPE_CHECKING:
    from typing_extensions import Self

T = TypeVar("T")


@dataclass
class ReadInstruction(Generic[T]):
    """Unified way to represent read instruction for both sync and async interface.

    This allows us to generate executable read operations for both synchronous and
    asynchronous readers, avoiding code repetition.
    """

    __slots__ = ("sync_func", "async_func")

    sync_func: Callable[[BaseSyncReader], T]
    async_func: Callable[[BaseAsyncReader], Awaitable[T]]

    @classmethod
    def n_bytes(cls, n: int) -> Self:
        """Produce a read instruction for reading n bytes."""
        sync_f = partial(BaseSyncReader.read, length=n)
        async_f = partial(BaseAsyncReader.read, length=n)
        return cls(sync_f, async_f)


BASIC_READ_INSTRUCTIONS: dict[str, ReadInstruction] = {
    "BOOL": ReadInstruction(BaseSyncReader.read_bool, BaseAsyncReader.read_bool),
    "BYTE": ReadInstruction(BaseSyncReader.read_byte, BaseAsyncReader.read_byte),
    "UBYTE": ReadInstruction(BaseSyncReader.read_ubyte, BaseAsyncReader.read_ubyte),
    "SHORT": ReadInstruction(BaseSyncReader.read_short, BaseAsyncReader.read_short),
    "USHORT": ReadInstruction(BaseSyncReader.read_ushort, BaseAsyncReader.read_ushort),
    "INT": ReadInstruction(BaseSyncReader.read_int, BaseAsyncReader.read_int),
    "UINT": ReadInstruction(BaseSyncReader.read_uint, BaseAsyncReader.read_uint),
    "LONG": ReadInstruction(BaseSyncReader.read_long, BaseAsyncReader.read_long),
    "ULONG": ReadInstruction(BaseSyncReader.read_ulong, BaseAsyncReader.read_ulong),
    "FLOAT": ReadInstruction(BaseSyncReader.read_float, BaseAsyncReader.read_float),
    "DOUBLE": ReadInstruction(BaseSyncReader.read_double, BaseAsyncReader.read_double),
    "VARSHORT": ReadInstruction(BaseSyncReader.read_varshort, BaseAsyncReader.read_varshort),
    "VARINT": ReadInstruction(BaseSyncReader.read_varint, BaseAsyncReader.read_varint),
    "VARLONG": ReadInstruction(BaseSyncReader.read_varlong, BaseAsyncReader.read_varlong),
    "UTF": ReadInstruction(BaseSyncReader.read_utf, BaseAsyncReader.read_utf),
    "BYTEARRAY": ReadInstruction(BaseSyncReader.read_bytearray, BaseAsyncReader.read_bytearray),
}


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

    _READ_INSTRUCTIONS: ClassVar[Sequence[ReadInstruction]]

    @classmethod
    @abstractmethod
    def _deserialize(cls, read_result: tuple) -> Self:
        ...

    @classmethod
    def read(cls, reader: BaseSyncReader) -> Self:
        read_result = tuple(instr.sync_func(reader) for instr in cls._READ_INSTRUCTIONS)
        return cls._deserialize(read_result)

    @classmethod
    async def async_read(cls, reader: BaseAsyncReader) -> Self:
        read_result = []
        for instruction in cls._READ_INSTRUCTIONS:
            res = await instruction.async_func(reader)
            read_result.append(res)
        return cls._deserialize(tuple(read_result))


class ReadWriteCapable(ReadCapable, WriteCapable):
    """Base class providing sync and async read+write capabilities."""
