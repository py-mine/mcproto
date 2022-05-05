from __future__ import annotations

import struct
from abc import ABC, abstractmethod
from ctypes import c_int16 as signed_int16
from ctypes import c_int32 as signed_int32
from ctypes import c_int64 as signed_int64
from ctypes import c_uint16 as unsigned_int16
from ctypes import c_uint32 as unsigned_int32
from ctypes import c_uint64 as unsigned_int64
from functools import wraps
from itertools import count
from typing import Any, Callable, Optional, TYPE_CHECKING, TypeVar, cast

if TYPE_CHECKING:
    from typing_extensions import ParamSpec

    P = ParamSpec("P")

T = TypeVar("T")
R = TypeVar("R")


def _enforce_range(*, typ: str, byte_size: Optional[int], signed: bool) -> Callable:
    """Decorator enforcing proper int value range, based on the number of bytes.

    If a value is outside of the automatically determined allowed range, a ValueError will be raised,
    showing the given `typ` along with the allowed range info.

    If the byte_size is None, infinite max size is assumed. Note that this is only possible with unsigned types,
    since there's no point in enforcing infinite range.
    """
    if byte_size is None:
        if signed is True:
            raise ValueError("Enforcing infinite byte-size for signed type doesn't make sense (includes all numbers).")
        value_max = float("inf")
        value_max_s = "infinity"
        value_min = 0
        value_min_s = "0"
    else:
        if signed:
            value_max = (1 << (byte_size * 8 - 1)) - 1
            value_max_s = f"{value_max} (2**{byte_size * 8 - 1} - 1)"
            value_min = -1 << (byte_size * 8 - 1)
            value_min_s = f"{value_min} (-2**{byte_size * 8 - 1})"
        else:
            value_max = (1 << (byte_size * 8)) - 1
            value_max_s = f"{value_max} (2**{byte_size * 8} - 1)"
            value_min = 0
            value_min_s = "0"

    def wrapper(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def inner(*args: P.args, **kwargs: P.kwargs) -> R:
            value = cast(int, args[1])
            if value > value_max or value < value_min:
                raise ValueError(f"{typ} must be within {value_min_s} and {value_max_s}, got {value}.")
            return func(*args, **kwargs)

        return inner

    return wrapper


class BaseWriter(ABC):
    """Base class holding write buffer/connection interactions."""

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

    @_enforce_range(typ="Byte (8-bit signed int)", byte_size=1, signed=True)
    def write_byte(self, value: int) -> None:
        """Write a single signed 8-bit integer.

        Signed 8-bit integers must be within the range of -128 and 127. Going outside this range will raise a
        ValueError.

        Number is written in two's complement format.
        """
        self._write_packed("b", value)

    @_enforce_range(typ="Unsigned byte (8-bit unsigned int)", byte_size=1, signed=False)
    def write_ubyte(self, value: int) -> None:
        """Write a single unsigned 8-bit integer.

        Unsigned 8-bit integers must be within range of 0 and 255. Going outside this range will raise a ValueError.
        """
        self._write_packed("B", value)

    @_enforce_range(typ="Short (16-bit signed int)", byte_size=2, signed=True)
    def write_short(self, value: int) -> None:
        """Write a signed 16-bit integer.

        Signed 16-bit integers must be within the range of -2**15 (-32768) and 2**15-1 (32767). Going outside this
        range will raise ValueError.

        Number is written in two's complement format.
        """
        self._write_packed("h", value)

    @_enforce_range(typ="Unsigned short (16-bit unsigned int)", byte_size=2, signed=False)
    def write_ushort(self, value: int) -> None:
        """Write an unsigned 16-bit integer.

        Unsigned 16-bit integers must be within the range of 0 and 2**16-1 (65535). Going outside this range will raise
        ValueError.
        """
        self._write_packed("H", value)

    @_enforce_range(typ="Int (32-bit signed int)", byte_size=4, signed=True)
    def write_int(self, value: int) -> None:
        """Write a signed 32-bit integer.

        Signed 32-bit integers must be within the range of -2**31 and 2**31-1. Going outside this range will
        raise ValueError.

        Number is written in two's complement format.
        """
        self._write_packed("i", value)

    @_enforce_range(typ="Unsigned int (32-bit unsigned int)", byte_size=4, signed=False)
    def write_uint(self, value: int) -> None:
        """Write an unsigned 32-bit integer.

        Unsigned 32-bit integers must be within the range of 0 and 2**32-1. Going outside this range will raise
        ValueError.
        """
        self._write_packed("I", value)

    @_enforce_range(typ="Long (64-bit signed int)", byte_size=8, signed=True)
    def write_long(self, value: int) -> None:
        """Write a signed 64-bit integer.

        Signed 64-bit integers must be within the range of -2**31 and 2**31-1. Going outside this range will raise
        ValueError.

        Number is written in two's complement format.
        """
        self._write_packed("q", value)

    @_enforce_range(typ="Long (64-bit unsigned int)", byte_size=8, signed=False)
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

    def _write_varnum(self, value: int, max_size: Optional[int] = None) -> None:
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
        # We can't use _enforce_range as decorator directly, because our byte_size varies
        # instead run it manually from here as a check function
        _wrapper = _enforce_range(
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

    @_enforce_range(typ="Varshort (variable length 16-bit signed int)", byte_size=2, signed=True)
    def write_varshort(self, value: int) -> None:
        """Write a 16-bit signed integer in a variable length format.

        Signed 16-bit integer varnums will never get over 3 bytes, and must be within the range of -2**15 and 2**15-1.
        """
        unsigned_form = unsigned_int16(value).value
        self._write_varnum(unsigned_form, max_size=2)

    @_enforce_range(typ="Varint (variable length 32-bit signed int)", byte_size=4, signed=True)
    def write_varint(self, value: int) -> None:
        """Write a 32-bit signed integer in a variable length format.

        Signed 32-bit integer varnums will never get over 5 bytes, and must be within the range of -2**31 and 2**31-1.
        Going outside this range will raise ValueError.
        """
        unsigned_form = unsigned_int32(value).value
        self._write_varnum(unsigned_form, max_size=4)

    @_enforce_range(typ="Varlong (variable length 64-bit signed int)", byte_size=8, signed=True)
    def write_varlong(self, value: int) -> None:
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


class BaseReader(ABC):
    """Base class holding read buffer/connection interactions."""

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

    def _read_varnum(self, max_size: Optional[int] = None) -> int:
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
                return result

        # This is here to meet type-checkers for int return type, but this code will never actually be reached
        raise Exception("Unreachable")

    def read_varshort(self) -> int:
        """Read a 16-bit signed integer in a variable length format.

        Will read 1 to 3 bytes, depending on the number, getting a corresponding 16-bit signed int value between -2**15
        and 2**15-1
        """
        unsigned = self._read_varnum(2)
        return signed_int16(unsigned).value

    def read_varint(self) -> int:
        """Read a 32-bit signed integer in a variable length format.

        Will read 1 to to 5 bytes, depending on the number, getting a corresponding 32-bit signed int value between
        -2**31 and 2**31-1.
        """
        unsigned = self._read_varnum(4)
        return signed_int32(unsigned).value

    def read_varlong(self) -> int:
        """Read a 64-bit signed integer in variable length format

        Will read 1 to 10 bytes, depending on the number, getting corresponding 64-bit signed int value between
        -2**63 and 2**63-1.
        """
        unsigned = self._read_varnum(8)
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
