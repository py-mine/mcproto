from unittest.mock import AsyncMock, Mock, patch

import pytest

from mcproto.protocol.abc import BaseSyncReader, BaseSyncWriter


class SyncWriter(BaseSyncWriter):
    """Testable concrete implementation of BaseSyncWriter ABC."""

    def __init__(self):
        self.data = bytearray()

    def write(self, data: bytearray) -> None:
        self.data.extend(data)


class SyncReader(BaseSyncReader):
    """Testable concrete implementation of BaseSyncReader ABC."""

    def __init__(self, data: bytearray):
        self.data = data

    def read(self, length: int) -> bytearray:
        data = self.data[:length]
        del self.data[:length]
        return data


def _to_two_complement(number: int, bytes: int) -> int:
    """Helper function to convert a number into two's complement format."""
    return number + 2 ** (bytes * 8)


def _from_two_complement(number: int, bytes: int) -> int:
    """Helper function to get the real value from int in two's complement format."""
    return number - 2 ** (bytes * 8) + 1


class TestBaseSyncWriter:
    """Tests for individual write methods implemented in BaseWriter."""

    @classmethod
    def setup_class(cls):
        cls.writer = SyncWriter()

    def setup_method(self):
        self.writer.data.clear()

    def test_write_byte(self):
        """Writing byte int should store an integer in a single byte."""
        self.writer.write_byte(15)
        assert self.writer.data == bytearray([15])

    def test_write_byte_negative(self):
        """Negative number bytes should be stored in two's complement format."""
        self.writer.write_byte(-20)
        assert self.writer.data == bytearray([_to_two_complement(-20, 1)])

    def test_write_byte_out_of_range(self):
        """Signed bytes should only allow writes from -128 to 127."""
        with pytest.raises(ValueError):
            self.writer.write_byte(-129)
        with pytest.raises(ValueError):
            self.writer.write_byte(128)

    def test_write_ubyte(self):
        """Writing unsigned byte int should store an integer in a single byte."""
        self.writer.write_byte(80)
        assert self.writer.data == bytearray([80])

    def test_write_ubyte_out_of_range(self):
        """Unsigned bytes should only allow writes from 0 to 255."""
        with pytest.raises(ValueError):
            self.writer.write_ubyte(256)
        with pytest.raises(ValueError):
            self.writer.write_ubyte(-1)

    # We skip over many similar single type write functions, these are mostly just wrappers around struct.pack,
    # and testing each function would get very repetetive with little benefit, considering struct library itself can be
    # trusted. Specifically, these left out functions are:
    # - write_bool
    # - write_short, write_ushort
    # - write_int, write_uint
    # - write_long, write_ulong
    # - write_float
    # - write_double
    # - write_varshort
    # - write_varlong

    @pytest.mark.parametrize(
        "number,expected_bytes",
        (
            (0, [0]),
            (1, [1]),
            (2, [2]),
            (15, [15]),
            (127, [127]),
            (128, [128, 1]),
            (129, [129, 1]),
            (255, [255, 1]),
            (1000000, [192, 132, 61]),
            (2147483647, [255, 255, 255, 255, 7]),
        ),
    )
    def test__write_varnum(self, number, expected_bytes):
        """Writing varnums results in correct bytes."""
        self.writer._write_varnum(number)
        assert self.writer.data == bytearray(expected_bytes)

    def test__write_varnum_out_of_range(self):
        """Varnums without max size should only work with positive integers."""
        with pytest.raises(ValueError):
            self.writer._write_varnum(-1)

    def test__write_varnum_max_size(self):
        """Varnums should be limitable to n max bytes and work with values in range."""
        self.writer._write_varnum(2**16 - 1, max_size=2)
        assert self.writer.data == bytearray([255, 255, 3])

    def test__write_varnum_max_size_out_of_range(self):
        """Varnums limited to n max bytes should raise ValueErrors for numbers out of this range."""
        with pytest.raises(ValueError):
            self.writer._write_varnum(2**16, max_size=2)

    @pytest.mark.parametrize(
        "varint_value,expected_varnum_call",
        (
            (0, 0),
            (120, 120),
            (2147483647, 2147483647),
            (-1, _to_two_complement(-1, 4)),
            (-2147483648, _to_two_complement(-2147483648, 4)),
        ),
    )
    def test_write_varint(self, varint_value, expected_varnum_call):
        """Writing varint should call _write_varnum with proper values."""
        mock_f = Mock()
        with patch("mcproto.protocol.abc.BaseSyncWriter._write_varnum", mock_f):
            self.writer.write_varint(varint_value)

        mock_f.assert_called_once_with(expected_varnum_call, max_size=4)

    @pytest.mark.parametrize("value", (-2147483649, 2147483648, 10**20, -(10**20)))
    def test_write_varint_out_of_range(self, value):
        """Writing varint outside of signed 32-bit int range should raise ValueError on it's own."""
        mock_f = Mock()
        with patch("mcproto.protocol.abc.BaseSyncWriter._write_varnum", mock_f):
            with pytest.raises(ValueError):
                self.writer.write_varint(value)
        # Range limitation should come from write_varint, not _write_varnum
        mock_f.assert_not_called()

    @pytest.mark.parametrize(
        "string,expected_bytes",
        (
            ("test", [len("test")] + list(map(ord, "test"))),
            ("a" * 100, [len("a" * 100)] + list(map(ord, "a" * 100))),
            ("", [0]),
        ),
    )
    def test_write_utf(self, string, expected_bytes):
        """Writing UTF string results in correct bytes."""
        self.writer.write_utf(string)
        assert self.writer.data == bytearray(expected_bytes)


class TestBaseSyncReader:
    """Tests for individual write methods implemented in BaseWriter."""

    @classmethod
    def setup_class(cls):
        cls.reader = SyncReader(bytearray())

    def setup_method(self):
        self.reader.data.clear()

    @pytest.mark.parametrize(
        "read_bytes,expected_value",
        (
            ([10], 10),
            ([255], 255),
            ([0], 0),
        ),
    )
    def test_read_ubyte(self, read_bytes, expected_value):
        """Reading byte int should return an integer in a single unsigned byte."""
        self.reader.data = bytearray(read_bytes)
        assert self.reader.read_ubyte() == expected_value

    @pytest.mark.parametrize(
        "read_bytes,expected_value",
        (
            ([_to_two_complement(-20, 1)], -20),
            ([_to_two_complement(-128, 1)], -128),
            ([20], 20),
            ([127], 127),
        ),
    )
    def test_read_byte(self, read_bytes, expected_value):
        """Negative number bytes should be read from two's complement format."""
        self.reader.data = bytearray(read_bytes)
        assert self.reader.read_byte() == expected_value

    # We skip over many similar single type write functions, these are mostly just wrappers around struct.pack,
    # and testing each function would get very repetetive with little benefit, considering struct library itself can be
    # trusted. Specifically, these left out functions are:
    # - read_bool
    # - read_short, read_ushort
    # - read_int, read_uint
    # - read_long, read_ulong
    # - read_float
    # - read_double
    # - read_varshort
    # - read_varlong

    @pytest.mark.parametrize(
        "read_bytes,expected_value",
        (
            ([0], 0),
            ([1], 1),
            ([2], 2),
            ([15], 15),
            ([127], 127),
            ([128, 1], 128),
            ([129, 1], 129),
            ([255, 1], 255),
            ([192, 132, 61], 1000000),
            ([255, 255, 255, 255, 7], 2147483647),
        ),
    )
    def test__read_varnum(self, read_bytes, expected_value):
        """Reading varnums bytes results in correct values."""
        self.reader.data = bytearray(read_bytes)
        assert self.reader._read_varnum() == expected_value

    def test__read_varnum_max_size(self):
        """Varnum reading should be limitable to n max bytes and work with values in range."""
        self.reader.data = bytearray([255, 255, 3])
        assert self.reader._read_varnum(max_size=2) == 2**16 - 1

    def test__read_varnum_max_size_out_of_range(self):
        """Varnum reading limited to n max bytes should raise an IOError for numbers out of this range."""
        self.reader.data = bytearray([128, 128, 4])
        with pytest.raises(IOError):
            self.reader._read_varnum(max_size=2)

    @pytest.mark.parametrize(
        "varnum_return_value,expected_varint_value",
        (
            (0, 0),
            (120, 120),
            (2147483647, 2147483647),
            (_to_two_complement(-1, 4), -1),
            (_to_two_complement(-2147483648, 4), -2147483648),
        ),
    )
    def test_read_varint(self, varnum_return_value, expected_varint_value):
        """Reading varint should convert result from _read_varnum into signed value."""
        # We need to support both sync and async calls here, so patch and mock both
        mock_f = Mock()
        mock_f.return_value = varnum_return_value
        async_mock_f = AsyncMock()
        async_mock_f.return_value = varnum_return_value
        with patch("mcproto.protocol.abc.BaseSyncReader._read_varnum", mock_f):
            with patch("mcproto.protocol.abc.BaseAsyncReader._read_varnum", async_mock_f):
                assert self.reader.read_varint() == expected_varint_value

        try:
            mock_f.assert_called_once_with(max_size=4)
        except AssertionError as exc:
            try:
                async_mock_f.assert_called_once_with(max_size=4)
            except TypeError:
                raise exc

    @pytest.mark.parametrize(
        "read_bytes,expected_string",
        (
            ([len("test")] + list(map(ord, "test")), "test"),
            ([len("a" * 100)] + list(map(ord, "a" * 100)), "a" * 100),
            ([0], ""),
        ),
    )
    def test_read_utf(self, read_bytes, expected_string):
        """Reading UTF string results in correct values."""
        self.reader.data = bytearray(read_bytes)
        assert self.reader.read_utf() == expected_string
