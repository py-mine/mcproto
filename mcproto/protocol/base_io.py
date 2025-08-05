from __future__ import annotations

import struct
from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from enum import Enum
from itertools import count
from typing import Literal, TypeVar, overload

from typing_extensions import TypeAlias

from mcproto.protocol.utils import from_twos_complement, to_twos_complement

__all__ = [
    "FLOAT_FORMATS_TYPE",
    "INT_FORMATS_TYPE",
    "BaseAsyncReader",
    "BaseAsyncWriter",
    "BaseSyncReader",
    "BaseSyncWriter",
    "StructFormat",
]

T = TypeVar("T")
R = TypeVar("R")


# region: Format types


class StructFormat(str, Enum):
    """All possible write/read struct types.

    See Also:
        [`struct`][struct] module documentation.
    """

    BOOL = "?"
    CHAR = "c"
    BYTE = "b"
    UBYTE = "B"
    SHORT = "h"
    USHORT = "H"
    INT = "i"
    UINT = "I"
    LONG = "l"
    ULONG = "L"
    FLOAT = "f"
    DOUBLE = "d"
    HALFFLOAT = "e"
    LONGLONG = "q"
    ULONGLONG = "Q"


INT_FORMATS_TYPE: TypeAlias = Literal[
    StructFormat.BYTE,
    StructFormat.UBYTE,
    StructFormat.SHORT,
    StructFormat.USHORT,
    StructFormat.INT,
    StructFormat.UINT,
    StructFormat.LONG,
    StructFormat.ULONG,
    StructFormat.LONGLONG,
    StructFormat.ULONGLONG,
]

FLOAT_FORMATS_TYPE: TypeAlias = Literal[
    StructFormat.FLOAT,
    StructFormat.DOUBLE,
    StructFormat.HALFFLOAT,
]

# endregion

# region: Writer classes


class BaseAsyncWriter(ABC):
    """Base class holding asynchronous write buffer/connection interactions."""

    __slots__ = ()

    @abstractmethod
    async def write(self, data: bytes | bytearray, /) -> None:
        """Underlying write method, sending/storing the data.

        All of the writer functions will eventually call this method.
        """

    @overload
    async def write_value(self, fmt: INT_FORMATS_TYPE, value: int, /) -> None: ...

    @overload
    async def write_value(self, fmt: FLOAT_FORMATS_TYPE, value: float, /) -> None: ...

    @overload
    async def write_value(self, fmt: Literal[StructFormat.BOOL], value: bool, /) -> None: ...

    @overload
    async def write_value(self, fmt: Literal[StructFormat.CHAR], value: str, /) -> None: ...

    async def write_value(self, fmt: StructFormat, value: object, /) -> None:
        """Write a given `value` as given struct format (`fmt`) in big-endian mode."""
        await self.write(struct.pack(">" + fmt.value, value))

    async def _write_varuint(self, value: int, /, *, max_bits: int | None = None) -> None:
        """Write an arbitrarily big unsigned integer in a variable length format.

        This is a standard way of transmitting ints, and it allows smaller numbers to take less bytes.

        Writing will be limited up to integer values of `max_bits` bits, and trying to write bigger values will raise
        a [`ValueError`][ValueError]. Note that setting `max_bits` to for example 32 bits doesn't mean that at most 4
        bytes will be sent, in this case it would actually take at most 5 bytes, due to the variable encoding overhead.

        Varints send bytes where 7 least significant bits are value bits, and the most significant bit is continuation
        flag bit. If this continuation bit is set (1), it indicates that there will be another varint byte sent after
        this one. The least significant group is written first, followed by each of the more significant groups, making
        varints little-endian, however in groups of 7 bits, not 8.
        """
        value_max = (1 << (max_bits)) - 1 if max_bits is not None else float("inf")
        if value < 0 or value > value_max:
            raise ValueError(f"Tried to write varint outside of the range of {max_bits}-bit int.")

        remaining = value
        while True:
            if remaining & ~0x7F == 0:  # final byte
                await self.write_value(StructFormat.UBYTE, remaining)
                return
            # Write only 7 least significant bits with the first bit being 1, marking there will be another byte
            await self.write_value(StructFormat.UBYTE, remaining & 0x7F | 0x80)
            # Subtract the value we've already sent (7 least significant bits)
            remaining >>= 7

    async def write_varint(self, value: int, /) -> None:
        """Write a 32-bit signed integer in a variable length format.

        For more information about variable length format check [`_write_varuint`][..].
        """
        val = to_twos_complement(value, bits=32)
        await self._write_varuint(val, max_bits=32)

    async def write_varlong(self, value: int, /) -> None:
        """Write a 64-bit signed integer in a variable length format.

        For more information about variable length format check [`_write_varuint`][..].
        """
        val = to_twos_complement(value, bits=64)
        await self._write_varuint(val, max_bits=64)

    async def write_bytearray(self, data: bytes | bytearray, /) -> None:
        """Write an arbitrary sequence of bytes, prefixed with a varint of it's size."""
        await self.write_varint(len(data))
        await self.write(data)

    async def write_ascii(self, value: str, /) -> None:
        """Write ISO-8859-1 encoded string, with NULL (0x00) at the end to indicate string end."""
        data = bytes(value, "ISO-8859-1")
        await self.write(data)
        await self.write(bytes([0]))

    async def write_utf(self, value: str, /) -> None:
        """Write a UTF-8 encoded string, prefixed with a varint of it's size (in bytes).

        The maximum amount of UTF-8 characters is limited to 32767.

        Individual UTF-8 characters can take up to 4 bytes, however most of the common ones take up less. Assuming the
        worst case of 4 bytes per every character, at most 131068 data bytes will be written + 3 additional bytes from
        the varint encoding overhead.

        Raises:
            ValueError: If the given string `value` has more characters than the allowed maximum (32767).
        """
        if len(value) > 32767:
            raise ValueError("Maximum character limit for writing strings is 32767 characters.")

        data = bytes(value, "utf-8")
        await self.write_varint(len(data))
        await self.write(data)

    async def write_optional(self, value: T | None, /, writer: Callable[[T], Awaitable[R]]) -> R | None:
        """Write a bool showing if a `value` is present, if so, also writes this value with `writer` function.

        * When `value` is `None`, a bool of `False` will be written, and `None` is returned.
        * When `value` is not `None`, a bool of `True` is written, after which the `writer` function is called,
          and the return value is forwarded.
        """
        if value is None:
            await self.write_value(StructFormat.BOOL, False)
            return None

        await self.write_value(StructFormat.BOOL, True)
        return await writer(value)


class BaseSyncWriter(ABC):
    """Base class holding synchronous write buffer/connection interactions."""

    __slots__ = ()

    @abstractmethod
    def write(self, data: bytes | bytearray, /) -> None:
        """Underlying write method, sending/storing the data.

        All of the writer functions will eventually call this method.
        """

    @overload
    def write_value(self, fmt: INT_FORMATS_TYPE, value: int, /) -> None: ...

    @overload
    def write_value(self, fmt: FLOAT_FORMATS_TYPE, value: float, /) -> None: ...

    @overload
    def write_value(self, fmt: Literal[StructFormat.BOOL], value: bool, /) -> None: ...

    @overload
    def write_value(self, fmt: Literal[StructFormat.CHAR], value: str, /) -> None: ...

    def write_value(self, fmt: StructFormat, value: object, /) -> None:
        """Write a given `value` as given struct format (`fmt`) in big-endian mode."""
        self.write(struct.pack(">" + fmt.value, value))

    def _write_varuint(self, value: int, /, *, max_bits: int | None = None) -> None:
        """Write an arbitrarily big unsigned integer in a variable length format.

        This is a standard way of transmitting ints, and it allows smaller numbers to take less bytes.

        Writing will be limited up to integer values of `max_bits` bits, and trying to write bigger values will raise
        a [`ValueError`][ValueError]. Note that setting `max_bits` to for example 32 bits doesn't mean that at most 4
        bytes will be sent, in this case it would actually take at most 5 bytes, due to the variable encoding overhead.

        Varints send bytes where 7 least significant bits are value bits, and the most significant bit is continuation
        flag bit. If this continuation bit is set (1), it indicates that there will be another varint byte sent after
        this one. The least significant group is written first, followed by each of the more significant groups, making
        varints little-endian, however in groups of 7 bits, not 8.
        """
        value_max = (1 << (max_bits)) - 1 if max_bits is not None else float("inf")
        if value < 0 or value > value_max:
            raise ValueError(f"Tried to write varint outside of the range of {max_bits}-bit int.")

        remaining = value
        while True:
            if remaining & ~0x7F == 0:  # final byte
                self.write_value(StructFormat.UBYTE, remaining)
                return
            # Write only 7 least significant bits with the first bit being 1, marking there will be another byte
            self.write_value(StructFormat.UBYTE, remaining & 0x7F | 0x80)
            # Subtract the value we've already sent (7 least significant bits)
            remaining >>= 7

    def write_varint(self, value: int, /) -> None:
        """Write a 32-bit signed integer in a variable length format.

        For more information about variable length format check [`_write_varuint`][..].
        """
        val = to_twos_complement(value, bits=32)
        self._write_varuint(val, max_bits=32)

    def write_varlong(self, value: int, /) -> None:
        """Write a 64-bit signed integer in a variable length format.

        For more information about variable length format check [`_write_varuint`][..].
        """
        val = to_twos_complement(value, bits=64)
        self._write_varuint(val, max_bits=64)

    def write_bytearray(self, data: bytes | bytearray, /) -> None:
        """Write an arbitrary sequence of bytes, prefixed with a varint of it's size."""
        self.write_varint(len(data))
        self.write(data)

    def write_ascii(self, value: str, /) -> None:
        """Write ISO-8859-1 encoded string, with NULL (0x00) at the end to indicate string end."""
        data = bytes(value, "ISO-8859-1")
        self.write(data)
        self.write(bytes([0]))

    def write_utf(self, value: str, /) -> None:
        """Write a UTF-8 encoded string, prefixed with a varint of it's size (in bytes).

        The maximum amount of UTF-8 characters is limited to 32767.

        Individual UTF-8 characters can take up to 4 bytes, however most of the common ones take up less. Assuming the
        worst case of 4 bytes per every character, at most 131068 data bytes will be written + 3 additional bytes from
        the varint encoding overhead.

        Raises:
            ValueError: If the given string `value` has more characters than the allowed maximum (32767).
        """
        if len(value) > 32767:
            raise ValueError("Maximum character limit for writing strings is 32767 characters.")

        data = bytes(value, "utf-8")
        self.write_varint(len(data))
        self.write(data)

    def write_optional(self, value: T | None, /, writer: Callable[[T], R]) -> R | None:
        """Write a bool showing if a `value` is present, if so, also writes this value with `writer` function.

        * When `value` is `None`, a bool of `False` will be written, and `None` is returned.
        * When `value` is not `None`, a bool of `True` is written, after which the `writer` function is called,
          and the return value is forwarded.
        """
        if value is None:
            self.write_value(StructFormat.BOOL, False)
            return None

        self.write_value(StructFormat.BOOL, True)
        return writer(value)


# endregion
# region: Reader classes


class BaseAsyncReader(ABC):
    """Base class holding asynchronous read buffer/connection interactions."""

    __slots__ = ()

    @abstractmethod
    async def read(self, length: int, /) -> bytes:
        """Underlying read method, obtaining the raw data.

        All of the reader functions will eventually call this method.
        """

    @overload
    async def read_value(self, fmt: INT_FORMATS_TYPE, /) -> int: ...

    @overload
    async def read_value(self, fmt: FLOAT_FORMATS_TYPE, /) -> float: ...

    @overload
    async def read_value(self, fmt: Literal[StructFormat.BOOL], /) -> bool: ...

    @overload
    async def read_value(self, fmt: Literal[StructFormat.CHAR], /) -> str: ...

    async def read_value(self, fmt: StructFormat, /) -> object:
        """Read a value as given struct format (`fmt`) in big-endian mode.

        The amount of bytes to read will be determined based on the struct format automatically.
        """
        length = struct.calcsize(fmt.value)
        data = await self.read(length)
        unpacked = struct.unpack(">" + fmt.value, data)
        return unpacked[0]

    async def _read_varuint(self, *, max_bits: int | None = None) -> int:
        """Read an arbitrarily big unsigned integer in a variable length format.

        This is a standard way of transmitting ints, and it allows smaller numbers to take less bytes.

        Reading will be limited up to integer values of `max_bits` bits, and trying to read bigger values will raise
        an [`IOError`][IOError]. Note that setting `max_bits` to for example 32 bits doesn't mean that at most 4 bytes
        will be read, in this case we would actually read at most 5 bytes, due to the variable encoding overhead.

        Varints send bytes where 7 least significant bits are value bits, and the most significant bit is continuation
        flag bit. If this continuation bit is set (1), it indicates that there will be another varint byte sent after
        this one. The least significant group is written first, followed by each of the more significant groups, making
        varints little-endian, however in groups of 7 bits, not 8.
        """
        value_max = (1 << (max_bits)) - 1 if max_bits is not None else float("inf")

        result = 0
        for i in count():
            byte = await self.read_value(StructFormat.UBYTE)
            # Read 7 least significant value bits in this byte, and shift them appropriately to be in the right place
            # then simply add them (OR) as additional 7 most significant bits in our result
            result |= (byte & 0x7F) << (7 * i)

            # Ensure that we stop reading and raise an error if the size gets over the maximum
            # (if the current amount of bits is higher than allowed size in bits)
            if result > value_max:
                raise IOError(f"Received varint was outside the range of {max_bits}-bit int.")

            # If the most significant bit is 0, we should stop reading
            if not byte & 0x80:
                break

        return result

    async def read_varint(self) -> int:
        """Read a 32-bit signed integer in a variable length format.

        For more information about variable length format check [`_read_varuint`][..].
        """
        unsigned_num = await self._read_varuint(max_bits=32)
        return from_twos_complement(unsigned_num, bits=32)

    async def read_varlong(self) -> int:
        """Read a 64-bit signed integer in a variable length format.

        For more information about variable length format check [`_read_varuint`][..].
        """
        unsigned_num = await self._read_varuint(max_bits=64)
        return from_twos_complement(unsigned_num, bits=64)

    async def read_bytearray(self, /) -> bytes:
        """Read an arbitrary sequence of bytes, prefixed with a varint of it's size."""
        length = await self.read_varint()
        return await self.read(length)

    async def read_ascii(self) -> str:
        """Read ISO-8859-1 encoded string, until we encounter NULL (0x00) at the end indicating string end."""
        # Keep reading bytes until we find NULL
        result = bytearray()
        while len(result) == 0 or result[-1] != 0:
            byte = await self.read(1)
            result.extend(byte)
        return result[:-1].decode("ISO-8859-1")

    async def read_utf(self) -> str:
        """Read a UTF-8 encoded string, prefixed with a varint of it's size (in bytes).

        The maximum amount of UTF-8 characters is limited to 32767.

        Individual UTF-8 characters can take up to 4 bytes, however most of the common ones take up less. Assuming the
        worst case of 4 bytes per every character, at most 131068 data bytes will be read + 3 additional bytes from
        the varint encoding overhead.

        Raises:
            IOError:
                * If the prefix varint is bigger than the maximum (131068) bytes, the string will not be read at all,
                  and [`IOError`][IOError] will be raised immediately.
                * If the received string has more than the maximum amount of characters (32767). Note that in this
                  case, the string will still get read in it's entirety, since it fits into the maximum bytes limit
                  (131068), which was simply read at once. This limitation is here only to replicate the behavior of
                  minecraft's implementation.
        """
        length = await self.read_varint()
        if length > 131068:
            raise IOError(f"Maximum read limit for utf strings is 131068 bytes, got {length}.")

        data = await self.read(length)
        chars = data.decode("utf-8")

        if len(chars) > 32767:
            raise IOError(f"Maximum read limit for utf strings is 32767 characters, got {len(chars)}.")

        return chars

    async def read_optional(self, reader: Callable[[], Awaitable[R]]) -> R | None:
        """Read a bool showing if a value is present, if so, also reads this value with `reader` function.

        * When `False` is read, the function will not read anything and `None` is returned.
        * When `True` is read, the `reader` function is called, and it's return value is forwarded.
        """
        if not await self.read_value(StructFormat.BOOL):
            return None

        return await reader()


class BaseSyncReader(ABC):
    """Base class holding synchronous read buffer/connection interactions."""

    __slots__ = ()

    @abstractmethod
    def read(self, length: int, /) -> bytes:
        """Underlying read method, obtaining the raw data.

        All of the reader functions will eventually call this method.
        """

    @overload
    def read_value(self, fmt: INT_FORMATS_TYPE, /) -> int: ...

    @overload
    def read_value(self, fmt: FLOAT_FORMATS_TYPE, /) -> float: ...

    @overload
    def read_value(self, fmt: Literal[StructFormat.BOOL], /) -> bool: ...

    @overload
    def read_value(self, fmt: Literal[StructFormat.CHAR], /) -> str: ...

    def read_value(self, fmt: StructFormat, /) -> object:
        """Read a value into given struct format in big-endian mode.

        The amount of bytes to read will be determined based on the struct format automatically.
        """
        length = struct.calcsize(fmt.value)
        data = self.read(length)
        unpacked = struct.unpack(">" + fmt.value, data)
        return unpacked[0]

    def _read_varuint(self, *, max_bits: int | None = None) -> int:
        """Read an arbitrarily big unsigned integer in a variable length format.

        This is a standard way of transmitting ints, and it allows smaller numbers to take less bytes.

        Reading will be limited up to integer values of `max_bits` bits, and trying to read bigger values will raise
        an [`IOError`][IOError]. Note that setting `max_bits` to for example 32 bits doesn't mean that at most 4 bytes
        will be read, in this case we would actually read at most 5 bytes, due to the variable encoding overhead.

        Varints send bytes where 7 least significant bits are value bits, and the most significant bit is continuation
        flag bit. If this continuation bit is set (1), it indicates that there will be another varint byte sent after
        this one. The least significant group is written first, followed by each of the more significant groups, making
        varints little-endian, however in groups of 7 bits, not 8.
        """
        value_max = (1 << (max_bits)) - 1 if max_bits is not None else float("inf")

        result = 0
        for i in count():
            byte = self.read_value(StructFormat.UBYTE)
            # Read 7 least significant value bits in this byte, and shift them appropriately to be in the right place
            # then simply add them (OR) as additional 7 most significant bits in our result
            result |= (byte & 0x7F) << (7 * i)

            # Ensure that we stop reading and raise an error if the size gets over the maximum
            # (if the current amount of bits is higher than allowed size in bits)
            if result > value_max:
                raise IOError(f"Received varint was outside the range of {max_bits}-bit int.")

            # If the most significant bit is 0, we should stop reading
            if not byte & 0x80:
                break

        return result

    def read_varint(self) -> int:
        """Read a 32-bit signed integer in a variable length format.

        For more information about variable length format check [`_read_varuint`][..].
        """
        unsigned_num = self._read_varuint(max_bits=32)
        return from_twos_complement(unsigned_num, bits=32)

    def read_varlong(self) -> int:
        """Read a 64-bit signed integer in a variable length format.

        For more information about variable length format check [`_read_varuint`][..].
        """
        unsigned_num = self._read_varuint(max_bits=64)
        return from_twos_complement(unsigned_num, bits=64)

    def read_bytearray(self) -> bytes:
        """Read an arbitrary sequence of bytes, prefixed with a varint of it's size."""
        length = self.read_varint()
        return self.read(length)

    def read_ascii(self) -> str:
        """Read ISO-8859-1 encoded string, until we encounter NULL (0x00) at the end indicating string end."""
        # Keep reading bytes until we find NULL
        result = bytearray()
        while len(result) == 0 or result[-1] != 0:
            byte = self.read(1)
            result.extend(byte)
        return result[:-1].decode("ISO-8859-1")

    def read_utf(self) -> str:
        """Read a UTF-8 encoded string, prefixed with a varint of it's size (in bytes).

        The maximum amount of UTF-8 characters is limited to 32767.

        Individual UTF-8 characters can take up to 4 bytes, however most of the common ones take up less. Assuming the
        worst case of 4 bytes per every character, at most 131068 data bytes will be read + 3 additional bytes from
        the varint encoding overhead.

        Raises:
            IOError:
                * If the prefix varint is bigger than the maximum (131068) bytes, the string will not be read at all,
                  and [`IOError`][IOError] will be raised immediately.
                * If the received string has more than the maximum amount of characters (32767). Note that in this
                  case, the string will still get read in it's entirety, since it fits into the maximum bytes limit
                  (131068), which was simply read at once. This limitation is here only to replicate the behavior of
                  minecraft's implementation.
        """
        length = self.read_varint()
        if length > 131068:
            raise IOError(f"Maximum read limit for utf strings is 131068 bytes, got {length}.")

        data = self.read(length)
        chars = data.decode("utf-8")

        if len(chars) > 32767:
            raise IOError(f"Maximum read limit for utf strings is 32767 characters, got {len(chars)}.")

        return chars

    def read_optional(self, reader: Callable[[], R]) -> R | None:
        """Read a bool showing if a value is present, if so, also reads this value with `reader` function.

        * When `False` is read, the function will not read anything and `None` is returned.
        * When `True` is read, the `reader` function is called, and it's return value is forwarded.
        """
        if not self.read_value(StructFormat.BOOL):
            return None

        return reader()


# endregion
