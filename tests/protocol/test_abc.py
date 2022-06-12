import inspect
from abc import ABC, abstractmethod
from typing import List, Union
from unittest.mock import AsyncMock, Mock

import pytest

from mcproto.protocol.abc import BaseAsyncReader, BaseAsyncWriter, BaseSyncReader, BaseSyncWriter
from tests.protocol.helpers import (
    ReadFunctionAsyncMock,
    ReadFunctionMock,
    SyncReader,
    SyncWriter,
    WrappedAsyncReader,
    WrappedAsyncWriter,
    WriteFunctionAsyncMock,
    WriteFunctionMock,
    to_two_complement,
)

# region: Abstract test classes


class WriterTests(ABC):
    """This class holds tests for both sync and async versions of writer."""

    writer: Union[BaseSyncWriter, BaseAsyncWriter]

    @classmethod
    @abstractmethod
    def setup_class(cls):
        """Initialize writer instance to be tested."""
        ...

    @pytest.fixture
    def method_mock(self) -> Union[Mock, AsyncMock]:
        """Returns the appropriate type of mock, supporting both sync and async modes."""
        if isinstance(self.writer, BaseSyncWriter):
            return Mock
        return AsyncMock

    @pytest.fixture
    def autopatch(self, monkeypatch: pytest.MonkeyPatch):
        """Returns a simple function, supporting patching both sync/async writer functions with appropriate mocks.

        This returned function takes in the name of the function to patch, and returns the mock object.
        This mock object will either be Mock, or AsyncMock instance, depending on whether we're in async or sync mode.
        """
        if isinstance(self.writer, SyncWriter):
            patch_path = "mcproto.protocol.abc.BaseSyncWriter"
            mock_type = Mock
        else:
            patch_path = "mcproto.protocol.abc.BaseAsyncWriter"
            mock_type = AsyncMock

        def autopatch(function_name: str) -> Union[Mock, AsyncMock]:
            mock_f = mock_type()
            monkeypatch.setattr(f"{patch_path}.{function_name}", mock_f)
            return mock_f

        return autopatch

    @pytest.fixture
    def write_mock(self, monkeypatch: pytest.MonkeyPatch):
        """Monkeypatch the write function with a mock which is returned."""
        if isinstance(self.writer, BaseSyncWriter):
            mock_f = WriteFunctionMock()
        else:
            mock_f = WriteFunctionAsyncMock()

        monkeypatch.setattr(self.writer.__class__, "write", mock_f)
        return mock_f

    def test_write_byte(self, write_mock: WriteFunctionMock):
        """Writing byte int should store an integer in a single byte."""
        self.writer.write_byte(15)
        write_mock.assert_has_data(bytearray([15]))

    def test_write_byte_negative(self, write_mock: WriteFunctionMock):
        """Negative number bytes should be stored in two's complement format."""
        self.writer.write_byte(-20)
        write_mock.assert_has_data(bytearray([to_two_complement(-20, 1)]))

    def test_write_byte_out_of_range(self):
        """Signed bytes should only allow writes from -128 to 127."""
        with pytest.raises(ValueError):
            self.writer.write_byte(-129)
        with pytest.raises(ValueError):
            self.writer.write_byte(128)

    def test_write_ubyte(self, write_mock: WriteFunctionMock):
        """Writing unsigned byte int should store an integer in a single byte."""
        self.writer.write_byte(80)
        write_mock.assert_has_data(bytearray([80]))

    def test_write_ubyte_out_of_range(self):
        """Unsigned bytes should only allow writes from 0 to 255."""
        with pytest.raises(ValueError):
            self.writer.write_ubyte(256)
        with pytest.raises(ValueError):
            self.writer.write_ubyte(-1)

    # We skip over many similar single type write functions, these are mostly just wrappers around struct.pack,
    # which we can trust will work, or functions only relying on other internal methods, which were already tested
    # and are hence trusted too. Testing each of these functions would get very repetetive with little to no benefit.
    # Specifically, these functions are:
    # - write_bool
    # - write_short, write_ushort
    # - write_int, write_uint
    # - write_long, write_ulong
    # - write_float
    # - write_double
    # - write_varshort
    # - write_varlong
    # - write_bytearray

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
    def test__write_varnum(self, number: int, expected_bytes: List[int], write_mock: WriteFunctionMock):
        """Writing varnums results in correct bytes."""
        self.writer._write_varnum(number)
        write_mock.assert_has_data(bytearray(expected_bytes))

    def test__write_varnum_out_of_range(self):
        """Varnums without max size should only work with positive integers."""
        with pytest.raises(ValueError):
            self.writer._write_varnum(-1)

    def test__write_varnum_max_size(self, write_mock: WriteFunctionMock):
        """Varnums should be limitable to n max bytes and work with values in range."""
        self.writer._write_varnum(2**16 - 1, max_size=2)
        write_mock.assert_has_data(bytearray([255, 255, 3]))

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
            (-1, to_two_complement(-1, 4)),
            (-2147483648, to_two_complement(-2147483648, 4)),
        ),
    )
    def test_write_varint(self, varint_value: int, expected_varnum_call: int, autopatch):
        """Writing varint should call _write_varnum with proper values."""
        mock_f = autopatch("_write_varnum")
        self.writer.write_varint(varint_value)

        mock_f.assert_called_once_with(expected_varnum_call, max_size=4)

    @pytest.mark.parametrize("value", (-2147483649, 2147483648, 10**20, -(10**20)))
    def test_write_varint_out_of_range(self, value: int, autopatch):
        """Writing varint outside of signed 32-bit int range should raise ValueError on it's own."""
        mock_f = autopatch("_write_varnum")
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
    def test_write_utf(self, string: str, expected_bytes: List[int], write_mock: WriteFunctionMock):
        """Writing UTF string results in correct bytes."""
        self.writer.write_utf(string)
        write_mock.assert_has_data(bytearray(expected_bytes))

    def test_write_optional_true(self, method_mock: Union[Mock, AsyncMock], write_mock: WriteFunctionMock):
        """Writing non-None value should write True and run the writer function."""
        mock_v = Mock()
        mock_f = method_mock()
        self.writer.write_optional(mock_f, mock_v)
        mock_f.assert_called_once_with(mock_v)
        write_mock.assert_has_data(bytearray([1]))

    def test_write_optional_false(self, method_mock: Union[Mock, AsyncMock], write_mock: WriteFunctionMock):
        """Writing None value should write False and skip running the writer function."""
        mock_f = method_mock()
        self.writer.write_optional(mock_f, None)
        mock_f.assert_not_called()
        write_mock.assert_has_data(bytearray([0]))


class ReaderTests(ABC):
    """This class holds tests for both sync and async versions of reader."""

    reader: Union[BaseSyncReader, BaseAsyncReader]

    @classmethod
    @abstractmethod
    def setup_class(cls):
        """Initialize reader instance to be tested."""
        ...

    @pytest.fixture
    def method_mock(self) -> Union[Mock, AsyncMock]:
        """Returns the appropriate type of mock, supporting both sync and async modes."""
        if isinstance(self.reader, BaseSyncReader):
            return Mock
        return AsyncMock

    @pytest.fixture
    def autopatch(self, monkeypatch: pytest.MonkeyPatch):
        """Returns a simple function, supporting patching both sync/async reader functions with appropriate mocks.

        This returned function takes in the name of the function to patch, and returns the mock object.
        This mock object will either be Mock, or AsyncMock instance, depending on whether we're in async or sync mode.
        """
        if isinstance(self.reader, SyncReader):
            patch_path = "mcproto.protocol.abc.BaseSyncReader"
            mock_type = Mock
        else:
            patch_path = "mcproto.protocol.abc.BaseAsyncReader"
            mock_type = AsyncMock

        def autopatch(function_name: str) -> Union[Mock, AsyncMock]:
            mock_f = mock_type()
            monkeypatch.setattr(f"{patch_path}.{function_name}", mock_f)
            return mock_f

        return autopatch

    @pytest.fixture
    def read_mock(self, monkeypatch: pytest.MonkeyPatch):
        """Monkeypatch the read function with a mock which is returned."""
        if isinstance(self.reader, SyncReader):
            mock_f = ReadFunctionMock()
        else:
            mock_f = ReadFunctionAsyncMock()
        monkeypatch.setattr(self.reader.__class__, "read", mock_f)
        yield mock_f
        # Run this assertion after the test, to ensure that all specified data
        # to be read, actually was read
        mock_f.assert_read_everything()

    @pytest.mark.parametrize(
        "read_bytes,expected_value",
        (
            ([10], 10),
            ([255], 255),
            ([0], 0),
        ),
    )
    def test_read_ubyte(self, read_bytes: List[int], expected_value: int, read_mock: ReadFunctionMock):
        """Reading byte int should return an integer in a single unsigned byte."""
        read_mock.combined_data = bytearray(read_bytes)
        assert self.reader.read_ubyte() == expected_value

    @pytest.mark.parametrize(
        "read_bytes,expected_value",
        (
            ([to_two_complement(-20, 1)], -20),
            ([to_two_complement(-128, 1)], -128),
            ([20], 20),
            ([127], 127),
        ),
    )
    def test_read_byte(self, read_bytes: List[int], expected_value: int, read_mock: ReadFunctionMock):
        """Negative number bytes should be read from two's complement format."""
        read_mock.combined_data = bytearray(read_bytes)
        assert self.reader.read_byte() == expected_value

    # We skip over many similar single type write functions, these are mostly just wrappers around struct.pack,
    # which we can trust will work, or functions only relying on other internal methods, which were already tested
    # and are hence trusted too. Testing each of these functions would get very repetetive with little to no benefit.
    # Specifically, these functions are:
    # - read_bool
    # - read_short, read_ushort
    # - read_int, read_uint
    # - read_long, read_ulong
    # - read_float
    # - read_double
    # - read_varshort
    # - read_varlong
    # - read_bytearray

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
    def test__read_varnum(self, read_bytes: List[int], expected_value: int, read_mock: ReadFunctionMock):
        """Reading varnums bytes results in correct values."""
        read_mock.combined_data = bytearray(read_bytes)
        assert self.reader._read_varnum() == expected_value

    def test__read_varnum_max_size(self, read_mock: ReadFunctionMock):
        """Varnum reading should be limitable to n max bytes and work with values in range."""
        read_mock.combined_data = bytearray([255, 255, 3])
        assert self.reader._read_varnum(max_size=2) == 2**16 - 1

    def test__read_varnum_max_size_out_of_range(self, read_mock: ReadFunctionMock):
        """Varnum reading limited to n max bytes should raise an IOError for numbers out of this range."""
        read_mock.combined_data = bytearray([128, 128, 4])
        with pytest.raises(IOError):
            self.reader._read_varnum(max_size=2)

    @pytest.mark.parametrize(
        "varnum_return_value,expected_varint_value",
        (
            (0, 0),
            (120, 120),
            (2147483647, 2147483647),
            (to_two_complement(-1, 4), -1),
            (to_two_complement(-2147483648, 4), -2147483648),
        ),
    )
    def test_read_varint(self, varnum_return_value: int, expected_varint_value: int, autopatch):
        """Reading varint should convert result from _read_varnum into signed value."""
        mock_f = autopatch("_read_varnum")
        mock_f.return_value = varnum_return_value
        assert self.reader.read_varint() == expected_varint_value

        mock_f.assert_called_once_with(max_size=4)

    @pytest.mark.parametrize(
        "read_bytes,expected_string",
        (
            ([len("test")] + list(map(ord, "test")), "test"),
            ([len("a" * 100)] + list(map(ord, "a" * 100)), "a" * 100),
            ([0], ""),
        ),
    )
    def test_read_utf(self, read_bytes: List[int], expected_string: str, read_mock: ReadFunctionMock):
        """Reading UTF string results in correct values."""
        read_mock.combined_data = bytearray(read_bytes)
        assert self.reader.read_utf() == expected_string

    def test_read_optional_true(self, method_mock: Union[Mock, AsyncMock], read_mock: ReadFunctionMock):
        """Reading optional should run reader function when first bool is True."""
        mock_f = method_mock()
        read_mock.combined_data = bytearray([1])
        self.reader.read_optional(mock_f)
        mock_f.assert_called_once_with()

    def test_read_optional_false(self, method_mock: Union[Mock, AsyncMock], read_mock: ReadFunctionMock):
        """Reading optional should not run reader function when first bool is False."""
        mock_f = method_mock()
        read_mock.combined_data = bytearray([0])
        self.reader.read_optional(mock_f)
        mock_f.assert_not_called()


# endregion
# region: Concrete test classes


class TestBaseSyncWriter(WriterTests):
    """Tests for individual write methods implemented in BaseSyncWriter."""

    @classmethod
    def setup_class(cls):
        """Initialize writer instance to be tested."""
        cls.writer = SyncWriter()


class TestBaseSyncReader(ReaderTests):
    """Tests for individual write methods implemented in BaseSyncReader."""

    @classmethod
    def setup_class(cls):
        """Initialize reader instance to be tested."""
        cls.reader = SyncReader()


class TestBaseAsyncWriter(WriterTests):
    """Tests for individual write methods implemented in BaseAsyncWriter."""

    writer: WrappedAsyncWriter

    @classmethod
    def setup_class(cls):
        cls.writer = WrappedAsyncWriter()

    @pytest.mark.parametrize(
        "async_function_name",
        (
            "write",
            "write_bool",
            "write_byte",
            "write_ubyte",
            "write_short",
            "write_ushort",
            "write_int",
            "write_uint",
            "write_long",
            "write_ulong",
            "write_float",
            "write_double",
            "_write_varnum",
            "write_varshort",
            "write_varint",
            "write_varlong",
            "write_utf",
            "write_optional",
            "write_bytearray",
        ),
    )
    def test_methods_are_async(self, async_function_name: str):
        """Because of the nature of this test class, we should ensure that all wrapped functions are actually async.

        This is because we're wrapping all of the async functions and converting them into synchronous ones, however
        if they already were synchronous for some reason and shouldn't have been, we wouldn't detect it.
        """
        expected_async_func = getattr(self.writer._writer, async_function_name)
        assert inspect.iscoroutinefunction(expected_async_func)


class TestBaseAsyncReader(ReaderTests):
    """Tests for individual write methods implemented in BaseAsyncReader."""

    reader: WrappedAsyncReader

    @classmethod
    def setup_class(cls):
        cls.reader = WrappedAsyncReader()

    @pytest.mark.parametrize(
        "async_function_name",
        (
            "read",
            "read_bool",
            "read_byte",
            "read_ubyte",
            "read_short",
            "read_ushort",
            "read_int",
            "read_uint",
            "read_long",
            "read_ulong",
            "read_float",
            "read_double",
            "_read_varnum",
            "read_varshort",
            "read_varint",
            "read_varlong",
            "read_utf",
            "read_optional",
            "read_bytearray",
        ),
    )
    def test_methods_are_async(self, async_function_name: str):
        """Because of the nature of this test class, we should ensure that all wrapped functions are actually async.

        This is because we're wrapping all of the async functions and converting them into synchronous ones, however
        if they already were synchronous for some reason and shouldn't have been, we wouldn't detect it.
        """
        expected_async_func = getattr(self.reader._reader, async_function_name)
        assert inspect.iscoroutinefunction(expected_async_func)


# endregion
