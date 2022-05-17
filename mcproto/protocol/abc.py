from __future__ import annotations

import struct
from abc import ABC, abstractmethod
from ctypes import c_int16 as signed_int16
from ctypes import c_int32 as signed_int32
from ctypes import c_int64 as signed_int64
from ctypes import c_uint16 as unsigned_int16
from ctypes import c_uint32 as unsigned_int32
from ctypes import c_uint64 as unsigned_int64
from itertools import count
from typing import Any, Awaitable, Callable, Optional, TypeVar, cast

from mcproto.protocol.utils import enforce_range

T = TypeVar("T")
R = TypeVar("R")


# region: Writer classes


class BaseAsyncWriter(ABC):
    """Base class holding asynchronous write buffer/connection interactions."""

    __slots__ = ()

    @abstractmethod
    async def write(self, data: bytes) -> None:
        ...

    async def _write_packed(self, fmt: str, *value: object) -> None:
        """Write a value of given struct format in big-endian mode.

        Available formats are listed in struct module's docstring.
        """
        await self.write(struct.pack(">" + fmt, *value))

    async def write_bool(self, value: bool) -> None:
        """Write a boolean True/False value.

        True is encoded as 0x01, while False is 0x00, both have a size of just 1 byte."""
        await self._write_packed("?", value)

    @enforce_range(typ="Byte (8-bit signed int)", byte_size=1, signed=True)
    async def write_byte(self, value: int) -> None:
        """Write a single signed 8-bit integer.

        Signed 8-bit integers must be within the range of -128 and 127. Going outside this range will raise a
        ValueError.

        Number is written in two's complement format.
        """
        await self._write_packed("b", value)

    @enforce_range(typ="Unsigned byte (8-bit unsigned int)", byte_size=1, signed=False)
    async def write_ubyte(self, value: int) -> None:
        """Write a single unsigned 8-bit integer.

        Unsigned 8-bit integers must be within range of 0 and 255. Going outside this range will raise a ValueError.
        """
        await self._write_packed("B", value)

    @enforce_range(typ="Short (16-bit signed int)", byte_size=2, signed=True)
    async def write_short(self, value: int) -> None:
        """Write a signed 16-bit integer.

        Signed 16-bit integers must be within the range of -2**15 (-32768) and 2**15-1 (32767). Going outside this
        range will raise ValueError.

        Number is written in two's complement format.
        """
        await self._write_packed("h", value)

    @enforce_range(typ="Unsigned short (16-bit unsigned int)", byte_size=2, signed=False)
    async def write_ushort(self, value: int) -> None:
        """Write an unsigned 16-bit integer.

        Unsigned 16-bit integers must be within the range of 0 and 2**16-1 (65535). Going outside this range will raise
        ValueError.
        """
        await self._write_packed("H", value)

    @enforce_range(typ="Int (32-bit signed int)", byte_size=4, signed=True)
    async def write_int(self, value: int) -> None:
        """Write a signed 32-bit integer.

        Signed 32-bit integers must be within the range of -2**31 and 2**31-1. Going outside this range will
        raise ValueError.

        Number is written in two's complement format.
        """
        await self._write_packed("i", value)

    @enforce_range(typ="Unsigned int (32-bit unsigned int)", byte_size=4, signed=False)
    async def write_uint(self, value: int) -> None:
        """Write an unsigned 32-bit integer.

        Unsigned 32-bit integers must be within the range of 0 and 2**32-1. Going outside this range will raise
        ValueError.
        """
        await self._write_packed("I", value)

    @enforce_range(typ="Long (64-bit signed int)", byte_size=8, signed=True)
    async def write_long(self, value: int) -> None:
        """Write a signed 64-bit integer.

        Signed 64-bit integers must be within the range of -2**31 and 2**31-1. Going outside this range will raise
        ValueError.

        Number is written in two's complement format.
        """
        await self._write_packed("q", value)

    @enforce_range(typ="Long (64-bit unsigned int)", byte_size=8, signed=False)
    async def write_ulong(self, value: int) -> None:
        """Write an unsigned 64-bit integer.

        Unsigned 64-bit integers must be within the range of 0 and 2**32-1. Going outside this range will raise
        ValueError.
        """
        await self._write_packed("Q", value)

    async def write_float(self, value: float) -> None:
        """Write a single precision 32-bit IEEE 754 floating point number.

        Checks for proper range requirement along with decimal precisions is NOT handled directly, and unlike most
        other write operations, will not result in a ValueError, instead packing will fail  and sturct.error will be
        raised. This is because it's quite difficult to actually check all conversion cases, and it's simple to just
        fail on packing.
        """
        await self._write_packed("f", value)

    async def write_double(self, value: float) -> None:
        """Write a double precision 64-bit IEEE 754 floating point number.

        Checks for proper range requirement along with decimal precisions is NOT handled directly, and unlike most
        other write operations, will not result in a ValueError, instead packing will fail  and sturct.error will be
        raised. This is because it's quite difficult to actually check all conversion cases, and it's simple to just
        fail on packing.
        """
        await self._write_packed("d", value)

    async def _write_varnum(self, value: int, *, max_size: Optional[int] = None) -> None:
        """Write an arbitrarily big unsigned integer in a variable length format.

        This is a standard way of transmitting ints, and it allows smaller numbers to take less bytes.

        Will keep writing bytes until the value is depleted (fully sent). If `max_size` is specified, writing will be
        limited up to integer values of max_size bytes, and trying to write bigger values will rase a ValueError. Note
        that limiting to max_size of 4 (32-bit int) doesn't imply at most 4 bytes will be sent, and will in fact take 5
        bytes at most, due to the variable encoding overhead.

        Varnums use 7 least significant bits of each sent byte to encode the value, and the most significant bit to
        indicate whether there is another byte after it. The least significant group is written first, followed by each
        of the more significant groups, making varints little-endian, however in groups of 7 bits, not 8.
        """
        # We can't use enforce_range as decorator directly, because our byte_size varies
        # instead run it manually from here as a check function
        _wrapper = enforce_range(
            typ=f"{max_size if max_size else 'unlimited'}-byte unsigned varnum",
            byte_size=max_size if max_size else None,
            signed=False,
        )
        _check_f = _wrapper(lambda self, value: None)
        _check_f(self, value)

        remaining = value
        while True:
            if remaining & ~0x7F == 0:  # final byte
                await self.write_ubyte(remaining)
                return
            # Write only 7 least significant bits with the first bit being 1, marking there will be another byte
            await self.write_ubyte(remaining & 0x7F | 0x80)
            # Subtract the value we've already sent (7 least significant bits)
            remaining >>= 7

    @enforce_range(typ="Varshort (variable length 16-bit signed int)", byte_size=2, signed=True)
    async def write_varshort(self, value: int) -> None:
        """Write a 16-bit signed integer in a variable length format.

        Signed 16-bit integer varnums will never get over 3 bytes, and must be within the range of -2**15 and 2**15-1.
        """
        unsigned_form = unsigned_int16(value).value
        await self._write_varnum(unsigned_form, max_size=2)

    @enforce_range(typ="Varint (variable length 32-bit signed int)", byte_size=4, signed=True)
    async def write_varint(self, value: int) -> None:
        """Write a 32-bit signed integer in a variable length format.

        Signed 32-bit integer varnums will never get over 5 bytes, and must be within the range of -2**31 and 2**31-1.
        Going outside this range will raise ValueError.
        """
        unsigned_form = unsigned_int32(value).value
        await self._write_varnum(unsigned_form, max_size=4)

    @enforce_range(typ="Varlong (variable length 64-bit signed int)", byte_size=8, signed=True)
    async def write_varlong(self, value: int) -> None:
        """Write a 64-bit signed integer in variable length format

        Signed 64-bit integer varnums will never get over 10 bytes, and must be within the range of -2**63 and 2**63-1.
        Going over this range will raise ValueError.
        """
        unsigned_form = unsigned_int64(value).value
        await self._write_varnum(unsigned_form, max_size=8)

    async def write_utf(self, value: str) -> None:
        """Write a UTF-8 encoded string, prefixed with a varshort of it's size (in bytes).

        Will write n bytes, depending on the amount of bytes in the string + up to 3 bytes from prefix varshort,
        holding this size (n). This means a maximum of 2**31-1 + 5 bytes can be written.

        Individual UTF-8 characters can take up to 4 bytes, however most of the common ones take up less. Assuming the
        worst case of 4 bytes per every character, at most 8192 characters can be written, however this number
        will usually be much bigger (up to 4x) since it's unlikely each character would actually take up 4 bytes. (All
        of the ASCII characters only take up 1 byte).

        If the given string is longer than this, ValueError will be raised for trying to write an invalid varshort.
        """
        data = bytearray(value, "utf-8")
        await self.write_varshort(len(data))
        await self.write(data)

    async def write_optional(self, writer: Callable[[T], Awaitable[R]], value: Optional[T] = None) -> Optional[R]:
        """Writes bool determining is value is present, if it is, also writes the value with writer function.

        When the `value` is None, a bool of False will be written and function will end. Otherwise, if `value` isn't
        None, True will be written, followed by calling the `writer` function wchich will be passed the `value` as the
        only argument. This function is expected to properly write the value into this buffer/connection.

        Will return None if the `value` was None, or the value returned by the `writer` function.
        """
        if value is None:
            await self.write_bool(False)
            return

        await self.write_bool(True)
        return await writer(value)


class BaseSyncWriter(ABC):
    """Base class holding synchronous write buffer/connection interactions."""

    __slots__ = ()

    @abstractmethod
    def write(self, data: bytes) -> None:
        ...

    def _write_packed(self, fmt: str, *value: object) -> None:
        """Write a value of given struct format in big-endian mode.

        Available formats are listed in struct module's docstring.
        """
        self.write(struct.pack(">" + fmt, *value))

    def write_bool(self, value: bool) -> None:
        """Write a boolean True/False value.

        True is encoded as 0x01, while False is 0x00, both have a size of just 1 byte."""
        self._write_packed("?", value)

    @enforce_range(typ="Byte (8-bit signed int)", byte_size=1, signed=True)
    def write_byte(self, value: int) -> None:
        """Write a single signed 8-bit integer.

        Signed 8-bit integers must be within the range of -128 and 127. Going outside this range will raise a
        ValueError.

        Number is written in two's complement format.
        """
        self._write_packed("b", value)

    @enforce_range(typ="Unsigned byte (8-bit unsigned int)", byte_size=1, signed=False)
    def write_ubyte(self, value: int) -> None:
        """Write a single unsigned 8-bit integer.

        Unsigned 8-bit integers must be within range of 0 and 255. Going outside this range will raise a ValueError.
        """
        self._write_packed("B", value)

    @enforce_range(typ="Short (16-bit signed int)", byte_size=2, signed=True)
    def write_short(self, value: int) -> None:
        """Write a signed 16-bit integer.

        Signed 16-bit integers must be within the range of -2**15 (-32768) and 2**15-1 (32767). Going outside this
        range will raise ValueError.

        Number is written in two's complement format.
        """
        self._write_packed("h", value)

    @enforce_range(typ="Unsigned short (16-bit unsigned int)", byte_size=2, signed=False)
    def write_ushort(self, value: int) -> None:
        """Write an unsigned 16-bit integer.

        Unsigned 16-bit integers must be within the range of 0 and 2**16-1 (65535). Going outside this range will raise
        ValueError.
        """
        self._write_packed("H", value)

    @enforce_range(typ="Int (32-bit signed int)", byte_size=4, signed=True)
    def write_int(self, value: int) -> None:
        """Write a signed 32-bit integer.

        Signed 32-bit integers must be within the range of -2**31 and 2**31-1. Going outside this range will
        raise ValueError.

        Number is written in two's complement format.
        """
        self._write_packed("i", value)

    @enforce_range(typ="Unsigned int (32-bit unsigned int)", byte_size=4, signed=False)
    def write_uint(self, value: int) -> None:
        """Write an unsigned 32-bit integer.

        Unsigned 32-bit integers must be within the range of 0 and 2**32-1. Going outside this range will raise
        ValueError.
        """
        self._write_packed("I", value)

    @enforce_range(typ="Long (64-bit signed int)", byte_size=8, signed=True)
    def write_long(self, value: int) -> None:
        """Write a signed 64-bit integer.

        Signed 64-bit integers must be within the range of -2**31 and 2**31-1. Going outside this range will raise
        ValueError.

        Number is written in two's complement format.
        """
        self._write_packed("q", value)

    @enforce_range(typ="Long (64-bit unsigned int)", byte_size=8, signed=False)
    def write_ulong(self, value: int) -> None:
        """Write an unsigned 64-bit integer.

        Unsigned 64-bit integers must be within the range of 0 and 2**32-1. Going outside this range will raise
        ValueError.
        """
        self._write_packed("Q", value)

    def write_float(self, value: float) -> None:
        """Write a single precision 32-bit IEEE 754 floating point number.

        Checks for proper range requirement along with decimal precisions is NOT handled directly, and unlike most
        other write operations, will not result in a ValueError, instead packing will fail  and sturct.error will be
        raised. This is because it's quite difficult to actually check all conversion cases, and it's simple to just
        fail on packing.
        """
        self._write_packed("f", value)

    def write_double(self, value: float) -> None:
        """Write a double precision 64-bit IEEE 754 floating point number.

        Checks for proper range requirement along with decimal precisions is NOT handled directly, and unlike most
        other write operations, will not result in a ValueError, instead packing will fail  and sturct.error will be
        raised. This is because it's quite difficult to actually check all conversion cases, and it's simple to just
        fail on packing.
        """
        self._write_packed("d", value)

    def _write_varnum(self, value: int, *, max_size: Optional[int] = None) -> None:
        """Write an arbitrarily big unsigned integer in a variable length format.

        This is a standard way of transmitting ints, and it allows smaller numbers to take less bytes.

        Will keep writing bytes until the value is depleted (fully sent). If `max_size` is specified, writing will be
        limited up to integer values of max_size bytes, and trying to write bigger values will rase a ValueError. Note
        that limiting to max_size of 4 (32-bit int) doesn't imply at most 4 bytes will be sent, and will in fact take 5
        bytes at most, due to the variable encoding overhead.

        Varnums use 7 least significant bits of each sent byte to encode the value, and the most significant bit to
        indicate whether there is another byte after it. The least significant group is written first, followed by each
        of the more significant groups, making varints little-endian, however in groups of 7 bits, not 8.
        """
        # We can't use enforce_range as decorator directly, because our byte_size varies
        # instead run it manually from here as a check function
        _wrapper = enforce_range(
            typ=f"{max_size if max_size else 'unlimited'}-byte unsigned varnum",
            byte_size=max_size if max_size else None,
            signed=False,
        )
        _check_f = _wrapper(lambda self, value: None)
        _check_f(self, value)

        remaining = value
        while True:
            if remaining & ~0x7F == 0:  # final byte
                self.write_ubyte(remaining)
                return
            # Write only 7 least significant bits with the first bit being 1, marking there will be another byte
            self.write_ubyte(remaining & 0x7F | 0x80)
            # Subtract the value we've already sent (7 least significant bits)
            remaining >>= 7

    @enforce_range(typ="Varshort (variable length 16-bit signed int)", byte_size=2, signed=True)
    def write_varshort(self, value: int) -> None:
        """Write a 16-bit signed integer in a variable length format.

        Signed 16-bit integer varnums will never get over 3 bytes, and must be within the range of -2**15 and 2**15-1.
        """
        unsigned_form = unsigned_int16(value).value
        self._write_varnum(unsigned_form, max_size=2)

    @enforce_range(typ="Varint (variable length 32-bit signed int)", byte_size=4, signed=True)
    def write_varint(self, value: int) -> None:
        """Write a 32-bit signed integer in a variable length format.

        Signed 32-bit integer varnums will never get over 5 bytes, and must be within the range of -2**31 and 2**31-1.
        Going outside this range will raise ValueError.
        """
        unsigned_form = unsigned_int32(value).value
        self._write_varnum(unsigned_form, max_size=4)

    @enforce_range(typ="Varlong (variable length 64-bit signed int)", byte_size=8, signed=True)
    async def write_varlong(self, value: int) -> None:
        """Write a 64-bit signed integer in variable length format

        Signed 64-bit integer varnums will never get over 10 bytes, and must be within the range of -2**63 and 2**63-1.
        Going over this range will raise ValueError.
        """
        unsigned_form = unsigned_int64(value).value
        self._write_varnum(unsigned_form, max_size=8)

    def write_utf(self, value: str) -> None:
        """Write a UTF-8 encoded string, prefixed with a varshort of it's size (in bytes).

        Will write n bytes, depending on the amount of bytes in the string + up to 3 bytes from prefix varshort,
        holding this size (n). This means a maximum of 2**31-1 + 5 bytes can be written.

        Individual UTF-8 characters can take up to 4 bytes, however most of the common ones take up less. Assuming the
        worst case of 4 bytes per every character, at most 8192 characters can be written, however this number
        will usually be much bigger (up to 4x) since it's unlikely each character would actually take up 4 bytes. (All
        of the ASCII characters only take up 1 byte).

        If the given string is longer than this, ValueError will be raised for trying to write an invalid varshort.
        """
        data = bytearray(value, "utf-8")
        self.write_varshort(len(data))
        self.write(data)

    def write_optional(self, writer: Callable[[T], R], value: Optional[T] = None) -> Optional[R]:
        """Writes bool determining is value is present, if it is, also writes the value with writer function.

        When the `value` is None, a bool of False will be written and function will end. Otherwise, if `value` isn't
        None, True will be written, followed by calling the `writer` function wchich will be passed the `value` as the
        only argument. This function is expected to properly write the value into this buffer/connection.

        Will return None if the `value` was None, or the value returned by the `writer` function.
        """
        if value is None:
            self.write_bool(False)
            return

        self.write_bool(True)
        return writer(value)


# endregion
# region: Reader classes


class BaseAsyncReader(ABC):
    """Base class holding asynchronous read buffer/connection interactions."""

    __slots__ = ()

    @abstractmethod
    async def read(self, length: int) -> bytearray:
        ...

    async def _read_unpacked(self, fmt: str) -> Any:  # noqa: ANN401
        """Read bytes and unpack them into given struct format in big-endian mode.


        The amount of bytes to read will be determined based on the format string automatically.
        i.e.: With format of "iii" (referring to 3 signed 32-bit ints), the read length is set as 3x4 (since a signed
            32-bit int takes 4 bytes), making the total length to read 12 bytes, returned as Tuple[int, int, int]

        Available formats are listed in struct module's docstring.
        """
        length = struct.calcsize(fmt)
        data = await self.read(length)
        unpacked = struct.unpack(">" + fmt, data)

        if len(unpacked) == 1:
            return unpacked[0]
        return unpacked

    async def read_bool(self) -> bool:
        """Read a boolean True/False value.

        Always reads 1 byte, with 0x01 being True and 0x00 being False.
        """
        return await self._read_unpacked("?")

    async def read_byte(self) -> int:
        """Read a single signed 8-bit integer.

        Will read 1 byte in two's complement format, getting int values between -128 and 127.
        """
        return await self._read_unpacked("b")

    async def read_ubyte(self) -> int:
        """Read a single unsigned 8-bit integer.

        Will read 1 byte, getting int value between 0 and 255 directly.
        """
        return await self._read_unpacked("B")

    async def read_short(self) -> int:
        """Read a signed 16-bit integer.

        Will read 2 bytes in two's complement format, getting int value between -2**15 (-32768) and 2**15-1 (32767)."""
        return await self._read_unpacked("h")

    async def read_ushort(self) -> int:
        """Read an unsigned 16-bit integer.

        Will read 2 bytes, getting int values between 0 and 2**16-1 (65535) directly.
        """
        return await self._read_unpacked("H")

    async def read_int(self) -> int:
        """Read a signed 32-bit integer.

        Will read 4 bytes in two's complement format, getting int values between -2**31 and 2**31-1.
        """
        return await self._read_unpacked("i")

    async def read_uint(self) -> int:
        """Read an unsigned 32-bit integer.

        Will read 4 bytes, getting int values between 0 and 2**31-1 directly.
        """
        return await self._read_unpacked("I")

    async def read_long(self) -> int:
        """Read a signed 64-bit integer.

        Will read 8 bytes in two's complement format, getting int values between -2**31 and 2**31-1.
        """
        return await self._read_unpacked("q")

    async def read_ulong(self) -> int:
        """Read an unsigned 64-bit integer.

        Will read 8 bytes, getting int  values between 0 and 2**32-1 directly.
        """
        return await self._read_unpacked("Q")

    async def read_float(self) -> float:
        """Read a single precision 32-bit IEEE 754 floating point number.

        Will read 4 bytes in IEEE 754 single precision float point number format, getting corresponding float values.
        """
        return await self._read_unpacked("f")

    async def read_double(self) -> float:
        """Read a double precision 64-bit IEEE 754 floating point number.

        Will read 8 bytes in IEEE 754 double precision float point number format, getting corresponding float values.
        """
        return await self._read_unpacked("d")

    async def _read_varnum(self, *, max_size: Optional[int] = None) -> int:
        """Read an arbitrarily big unsigned integer in a variable length format.

        This is a standard way of transmitting ints, and it allows smaller numbers to take less bytes.

        Will keep reading bytes until the value is depleted (fully sent). If `max_size` is specified, reading will be
        limited up to integer values of max_size bytes, and trying to read bigger values will rase an IOError. Note
        that limiting to max_size of 4 (32-bit int) doesn't imply at most 4 bytes will be sent, and will in fact take 5
        bytes at most, due to the variable encoding overhead.

        Varnums use 7 least significant bits of each sent byte to encode the value, and the most significant bit to
        indicate whether there is another byte after it. The least significant group is written first, followed by each
        of the more significant groups, making varints little-endian, however in groups of 7 bits, not 8.
        """
        value_max = (1 << (max_size * 8)) - 1 if max_size else None
        result = 0
        for i in count():
            byte = await self.read_ubyte()
            # Read 7 least significant value bits in this byte, and shift them appropriately to be in the right place
            # then simply add them (OR) as additional 7 most significant bits in our result
            result |= (byte & 0x7F) << (7 * i)

            # Ensure that we stop reading and raise an error if the size gets over the maximum
            # (if the current amount of bits is higher than allowed size in bits)
            if value_max and result > value_max:
                max_size = cast(int, max_size)
                raise IOError(f"Received varint was outside the range of {max_size}-byte ({max_size * 8}-bit) int.")

            # If the most significant bit is 0, we should stop reading
            if not byte & 0x80:
                break

        return result

    async def read_varshort(self) -> int:
        """Read a 16-bit signed integer in a variable length format.

        Will read 1 to 3 bytes, depending on the number, getting a corresponding 16-bit signed int value between -2**15
        and 2**15-1
        """
        unsigned = await self._read_varnum(max_size=2)
        return signed_int16(unsigned).value

    async def read_varint(self) -> int:
        """Read a 32-bit signed integer in a variable length format.

        Will read 1 to to 5 bytes, depending on the number, getting a corresponding 32-bit signed int value between
        -2**31 and 2**31-1.
        """
        unsigned = await self._read_varnum(max_size=4)
        return signed_int32(unsigned).value

    async def read_varlong(self) -> int:
        """Read a 64-bit signed integer in variable length format

        Will read 1 to 10 bytes, depending on the number, getting corresponding 64-bit signed int value between
        -2**63 and 2**63-1.
        """
        unsigned = await self._read_varnum(max_size=8)
        return signed_int64(unsigned).value

    async def read_utf(self) -> str:
        """Read a UTF-8 encoded string, prefixed with a varshort of it's size (in bytes).

        Will read n bytes, depending on the prefix varint (amount of bytes in the string) + up to 3 bytes from prefix
        varshort itself, holding this size (n). This means a maximum of 2**15-1 + 3 bytes can be read (and written).

        Individual UTF-8 characters can take up to 4 bytes, however most of the common ones take up less. Assuming the
        worst case of 4 bytes per every character, at most 8192 characters can be written, however this number
        will usually be much bigger (up to 4x) since it's unlikely each character would actually take up 4 bytes. (All
        of the ASCII characters only take up 1 byte).
        """
        length = await self.read_varshort()
        print(length)
        bytes = await self.read(length)
        print(bytes)
        return bytes.decode("utf-8")

    async def read_optional(self, reader: Callable[[], Awaitable[R]]) -> Optional[R]:
        """Reads bool determining is value is present, if it is, also reads the value with reader function.

        When False is read, the function will not read anything and end. Otherwise, if True is read, the `reader`
        function will be called, which is expected to properly read the value from this buffer/connection.

        Will return None if the False was encountered, or the value returned by the `reader` function.
        """
        if not await self.read_bool():
            return

        return await reader()


class BaseSyncReader(ABC):
    """Base class holding synchronous read buffer/connection interactions."""

    __slots__ = ()

    @abstractmethod
    def read(self, length: int) -> bytearray:
        ...

    def _read_unpacked(self, fmt: str) -> Any:  # noqa: ANN401
        """Read bytes and unpack them into given struct format in big-endian mode.


        The amount of bytes to read will be determined based on the format string automatically.
        i.e.: With format of "iii" (referring to 3 signed 32-bit ints), the read length is set as 3x4 (since a signed
            32-bit int takes 4 bytes), making the total length to read 12 bytes, returned as Tuple[int, int, int]

        Available formats are listed in struct module's docstring.
        """
        length = struct.calcsize(fmt)
        data = self.read(length)
        unpacked = struct.unpack(">" + fmt, data)

        if len(unpacked) == 1:
            return unpacked[0]
        return unpacked

    def read_bool(self) -> bool:
        """Read a boolean True/False value.

        Always reads 1 byte, with 0x01 being True and 0x00 being False.
        """
        return self._read_unpacked("?")

    def read_byte(self) -> int:
        """Read a single signed 8-bit integer.

        Will read 1 byte in two's complement format, getting int values between -128 and 127.
        """
        return self._read_unpacked("b")

    def read_ubyte(self) -> int:
        """Read a single unsigned 8-bit integer.

        Will read 1 byte, getting int value between 0 and 255 directly.
        """
        return self._read_unpacked("B")

    def read_short(self) -> int:
        """Read a signed 16-bit integer.

        Will read 2 bytes in two's complement format, getting int value between -2**15 (-32768) and 2**15-1 (32767)."""
        return self._read_unpacked("h")

    def read_ushort(self) -> int:
        """Read an unsigned 16-bit integer.

        Will read 2 bytes, getting int values between 0 and 2**16-1 (65535) directly.
        """
        return self._read_unpacked("H")

    def read_int(self) -> int:
        """Read a signed 32-bit integer.

        Will read 4 bytes in two's complement format, getting int values between -2**31 and 2**31-1.
        """
        return self._read_unpacked("i")

    def read_uint(self) -> int:
        """Read an unsigned 32-bit integer.

        Will read 4 bytes, getting int values between 0 and 2**31-1 directly.
        """
        return self._read_unpacked("I")

    def read_long(self) -> int:
        """Read a signed 64-bit integer.

        Will read 8 bytes in two's complement format, getting int values between -2**31 and 2**31-1.
        """
        return self._read_unpacked("q")

    def read_ulong(self) -> int:
        """Read an unsigned 64-bit integer.

        Will read 8 bytes, getting int  values between 0 and 2**32-1 directly.
        """
        return self._read_unpacked("Q")

    def read_float(self) -> float:
        """Read a single precision 32-bit IEEE 754 floating point number.

        Will read 4 bytes in IEEE 754 single precision float point number format, getting corresponding float values.
        """
        return self._read_unpacked("f")

    def read_double(self) -> float:
        """Read a double precision 64-bit IEEE 754 floating point number.

        Will read 8 bytes in IEEE 754 double precision float point number format, getting corresponding float values.
        """
        return self._read_unpacked("d")

    def _read_varnum(self, *, max_size: Optional[int] = None) -> int:
        """Read an arbitrarily big unsigned integer in a variable length format.

        This is a standard way of transmitting ints, and it allows smaller numbers to take less bytes.

        Will keep reading bytes until the value is depleted (fully sent). If `max_size` is specified, reading will be
        limited up to integer values of max_size bytes, and trying to read bigger values will rase an IOError. Note
        that limiting to max_size of 4 (32-bit int) doesn't imply at most 4 bytes will be sent, and will in fact take 5
        bytes at most, due to the variable encoding overhead.

        Varnums use 7 least significant bits of each sent byte to encode the value, and the most significant bit to
        indicate whether there is another byte after it. The least significant group is written first, followed by each
        of the more significant groups, making varints little-endian, however in groups of 7 bits, not 8.
        """
        value_max = (1 << (max_size * 8)) - 1 if max_size else None
        result = 0
        for i in count():
            byte = self.read_ubyte()
            # Read 7 least significant value bits in this byte, and shift them appropriately to be in the right place
            # then simply add them (OR) as additional 7 most significant bits in our result
            result |= (byte & 0x7F) << (7 * i)

            # Ensure that we stop reading and raise an error if the size gets over the maximum
            # (if the current amount of bits is higher than allowed size in bits)
            if value_max and result > value_max:
                max_size = cast(int, max_size)
                raise IOError(f"Received varint was outside the range of {max_size}-byte ({max_size * 8}-bit) int.")

            # If the most significant bit is 0, we should stop reading
            if not byte & 0x80:
                break

        return result

    def read_varshort(self) -> int:
        """Read a 16-bit signed integer in a variable length format.

        Will read 1 to 3 bytes, depending on the number, getting a corresponding 16-bit signed int value between -2**15
        and 2**15-1
        """
        unsigned = self._read_varnum(max_size=2)
        return signed_int16(unsigned).value

    def read_varint(self) -> int:
        """Read a 32-bit signed integer in a variable length format.

        Will read 1 to to 5 bytes, depending on the number, getting a corresponding 32-bit signed int value between
        -2**31 and 2**31-1.
        """
        unsigned = self._read_varnum(max_size=4)
        return signed_int32(unsigned).value

    def read_varlong(self) -> int:
        """Read a 64-bit signed integer in variable length format

        Will read 1 to 10 bytes, depending on the number, getting corresponding 64-bit signed int value between
        -2**63 and 2**63-1.
        """
        unsigned = self._read_varnum(max_size=8)
        return signed_int64(unsigned).value

    def read_utf(self) -> str:
        """Read a UTF-8 encoded string, prefixed with a varshort of it's size (in bytes).

        Will read n bytes, depending on the prefix varint (amount of bytes in the string) + up to 3 bytes from prefix
        varshort itself, holding this size (n). This means a maximum of 2**15-1 + 3 bytes can be read (and written).

        Individual UTF-8 characters can take up to 4 bytes, however most of the common ones take up less. Assuming the
        worst case of 4 bytes per every character, at most 8192 characters can be written, however this number
        will usually be much bigger (up to 4x) since it's unlikely each character would actually take up 4 bytes. (All
        of the ASCII characters only take up 1 byte).
        """
        length = self.read_varshort()
        bytes = self.read(length)
        return bytes.decode("utf-8")

    def read_optional(self, reader: Callable[[], R]) -> Optional[R]:
        """Reads bool determining is value is present, if it is, also reads the value with reader function.

        When False is read, the function will not read anything and end. Otherwise, if True is read, the `reader`
        function will be called, which is expected to properly read the value from this buffer/connection.

        Will return None if the False was encountered, or the value returned by the `reader` function.
        """
        if not self.read_bool():
            return

        return reader()


# endregion
