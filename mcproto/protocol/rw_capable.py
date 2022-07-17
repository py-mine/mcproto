from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable, Sequence
from dataclasses import dataclass
from functools import partial
from typing import ClassVar, Generic, Literal, TYPE_CHECKING, TypeVar, cast, overload

from mcproto.protocol.base_io import (
    BaseAsyncReader,
    BaseAsyncWriter,
    BaseSyncReader,
    BaseSyncWriter,
    FLOAT_FORMATS_TYPE,
    INT_FORMATS_TYPE,
    StructFormat,
)

if TYPE_CHECKING:
    from typing_extensions import Self

T = TypeVar("T")
R = TypeVar("R")

__all__ = [
    "ReadInstruction",
    "ReadCapable",
    "WriteCapable",
    "ReadWriteCapable",
]


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
    def n_bytes(cls, n: int) -> ReadInstruction[bytearray]:
        """Produce a read instruction for reading n bytes."""
        sync_f = partial(BaseSyncReader.read, length=n)
        async_f = partial(BaseAsyncReader.read, length=n)
        obj = cls(sync_f, async_f)
        return cast(ReadInstruction[bytearray], obj)

    @overload
    @classmethod
    def value(cls, fmt: INT_FORMATS_TYPE) -> ReadInstruction[int]:
        ...

    @overload
    @classmethod
    def value(cls, fmt: FLOAT_FORMATS_TYPE) -> ReadInstruction[float]:
        ...

    @overload
    @classmethod
    def value(cls, fmt: Literal[StructFormat.BOOL]) -> ReadInstruction[bool]:
        ...

    @overload
    @classmethod
    def value(cls, fmt: Literal[StructFormat.CHAR]) -> ReadInstruction[str]:
        ...

    @classmethod
    def value(cls, fmt: StructFormat) -> ReadInstruction:
        """Produce a read instruction for reading value of given format."""
        sync_f = partial(BaseSyncReader.read_value, fmt)
        async_f = partial(BaseAsyncReader.read_value, fmt)
        obj = cls(sync_f, async_f)
        return obj

    @classmethod
    def varint(cls, max_bits: int) -> ReadInstruction[int]:
        """Produce a read instruction for reading max_bits sized varint."""
        sync_f = partial(BaseSyncReader.read_varint, max_bits=max_bits)
        async_f = partial(BaseAsyncReader.read_varint, max_bits=max_bits)
        obj = cls(sync_f, async_f)
        return cast(ReadInstruction[int], obj)

    @classmethod
    def utf(cls) -> ReadInstruction[str]:
        """Produce a read instruction for reading UTF-8 encoded string."""
        sync_f = BaseSyncReader.read_utf
        async_f = BaseAsyncReader.read_utf
        obj = cls(sync_f, async_f)
        return cast(ReadInstruction[str], obj)

    def compound(self, instr_factory: Callable[[T], ReadInstruction[R]]) -> ReadInstruction[R]:
        """Generate a new instruction which relies on the result from this instruction.

        This function expects a instruction factory function, which returns a new ReadInstruction based on
        the input argument passed into it. This input arguments will be forwarded from the current instruction's
        reader function return.
        """

        def new_sync_func(reader: BaseSyncReader) -> R:
            intermediate = self.sync_func(reader)
            new_instr = instr_factory(intermediate)
            return new_instr.sync_func(reader)

        async def new_async_func(reader: BaseAsyncReader) -> R:
            intermediate = await self.async_func(reader)
            new_instr = instr_factory(intermediate)
            return await new_instr.async_func(reader)

        return ReadInstruction(new_sync_func, new_async_func)


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
