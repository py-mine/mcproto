from __future__ import annotations

import platform
import struct
import sys
from abc import ABC, abstractmethod
from typing import Any, Generic, TYPE_CHECKING, TypeVar, Union
from unittest.mock import AsyncMock, Mock

import pytest
from typing_extensions import override

from mcproto.protocol.base_io import (
    BaseAsyncReader,
    BaseAsyncWriter,
    BaseSyncReader,
    BaseSyncWriter,
    INT_FORMATS_TYPE,
    StructFormat,
)
from mcproto.protocol.utils import to_twos_complement
from tests.helpers import SynchronizedMixin
from tests.mcproto.protocol.helpers import (
    ReadFunctionAsyncMock,
    ReadFunctionMock,
    WriteFunctionAsyncMock,
    WriteFunctionMock,
)

# region: Initializable concrete implementations of ABC classes.


class SyncWriter(BaseSyncWriter):
    """Initializable concrete implementation of :class:`~mcproto.protocol.base_io.BaseSyncWriter` ABC."""

    @override
    def write(self, data: bytes) -> None:
        """Concrete implementation of abstract write method.

        Since :class:`abc.ABC` classes can't be initialized if they have any abstract methods
        which weren't overridden with a concrete implementations, this is a fake implementation,
        without any actual logic, purely to allow the initialization of this class.

        This method is expected to be mocked using :class:`~tests.mcproto.protocol.helpers.WriteFunctionMock`
        if it's supposed to get called during testing.

        If this method gets called without being mocked, it will raise :exc:`NotImplementedError`.
        """
        raise NotImplementedError(
            "This concrete override of abstract write method isn't intended for actual use!\n"
            " - If you're writing a new test, did you forget to mock it?\n"
            " - If you're seeing this in an existing test, this method got called without the test expecting it,"
            " this probably means you changed something in the code leading to this call, but you haven't updated"
            " the tests to mock this function."
        )


class SyncReader(BaseSyncReader):
    """Testable concrete implementation of :class:`~mcproto.protocol.base_io.BaseSyncReader` ABC."""

    @override
    def read(self, length: int) -> bytearray:
        """Concrete implementation of abstract read method.

        Since :class:`abc.ABC` classes can't be initialized if they have any abstract methods
        which weren't overridden with a concrete implementations, this is a fake implementation,
        without any actual logic, purely to allow the initialization of this class.

        This method is expected to be mocked using :class:`~tests.mcproto.protocol.helpers.ReadFunctionMock`
        if it's supposed to get called during testing.

        If this method gets called without being mocked, it will raise :exc:`NotImplementedError`.
        """
        raise NotImplementedError(
            "This concrete override of abstract read method isn't intended for actual use!\n"
            " - If you're writing a new test, did you forget to mock it?\n"
            " - If you're seeing this in an existing test, this method got called without the test expecting it,"
            " this probably means you changed something in the code leading to this call, but you haven't updated"
            " the tests to mock this function."
        )


class AsyncWriter(BaseAsyncWriter):
    """Initializable concrete implementation of :class:`~mcproto.protocol.base_io.BaseAsyncWriter` ABC."""

    @override
    async def write(self, data: bytes) -> None:
        """Concrete implementation of abstract write method.

        Since :class:`abc.ABC` classes can't be initialized if they have any abstract methods
        which weren't overridden with a concrete implementations, this is a fake implementation,
        without any actual logic, purely to allow the initialization of this class.

        This method is expected to be mocked using :class:`~tests.mcproto.protocol.helpers.WriteFunctionAsyncMock`
        if it's supposed to get called during testing.

        If this method gets called without being mocked, it will raise :exc:`NotImplementedError`.
        """
        raise NotImplementedError(
            "This concrete override of abstract write method isn't intended for actual use!\n"
            " - If you're writing a new test, did you forget to mock it?\n"
            " - If you're seeing this in an existing test, this method got called without the test expecting it,"
            " this probably means you changed something in the code leading to this call, but you haven't updated"
            " the tests to mock this function."
        )


class AsyncReader(BaseAsyncReader):
    """Testable concrete implementation of BaseAsyncReader ABC."""

    @override
    async def read(self, length: int) -> bytearray:
        """Concrete implementation of abstract read method.

        Since :class:`abc.ABC` classes can't be initialized if they have any abstract methods
        which weren't overridden with a concrete implementations, this is a fake implementation,
        without any actual logic, purely to allow the initialization of this class.

        This method is expected to be mocked using :class:`~tests.mcproto.protocol.helpers.ReadFunctionAsyncMock`
        if it's supposed to get called during testing.

        If this method gets called without being mocked, it will raise :exc:`NotImplementedError`.
        """
        raise NotImplementedError(
            "This concrete override of abstract read method isn't intended for actual use!\n"
            " - If you're writing a new test, did you forget to mock it?\n"
            " - If you're seeing this in an existing test, this method got called without the test expecting it,"
            " this probably means you changed something in the code leading to this call, but you haven't updated"
            " the tests to mock this function."
        )


# endregion
# region: Synchronized classes


class WrappedAsyncReader(SynchronizedMixin):
    """Wrapped synchronous implementation of asynchronous :class:`.AsyncReader` class.

    This essentially mimics :class:`~mcproto.protocol.base_io.BaseSyncReader`.
    """

    _WRAPPED_ATTRIBUTE = "_reader"

    def __init__(self):
        self._reader = AsyncReader()


class WrappedAsyncWriter(SynchronizedMixin):
    """Wrapped synchronous implementation of asynchronous :class:`.AsyncWriter` class.

    This essentially mimics :class:`~mcproto.protocol.base_io.BaseSyncWriter`.
    """

    _WRAPPED_ATTRIBUTE = "_writer"

    def __init__(self):
        self._writer = AsyncWriter()


# endregion
# region: Abstract test classes

T_WRITER = TypeVar("T_WRITER", bound=Union[BaseSyncWriter, BaseAsyncWriter])
T_READER = TypeVar("T_READER", bound=Union[BaseSyncReader, BaseAsyncReader])


# Pytest doesn't like test classes having __new__ in older python versions
# this is very hacky workaround, to have pytest recognize these classes when
# running on these older versions.
if sys.version_info > (3, 9) or TYPE_CHECKING:
    abc = ABC
    generic = Generic
else:
    abc = type("abc", (), {})
    generic = {T_WRITER: type("X", (), {}), T_READER: type("Y", (), {})}  # so generic indeed


class WriterTests(abc, generic[T_WRITER]):
    """Collection of tests for both sync and async versions of the writer."""

    writer: T_WRITER

    @classmethod
    @abstractmethod
    def setup_class(cls):
        """Initialize writer instance to be tested."""
        ...

    @pytest.fixture()
    def method_mock(self) -> Mock | AsyncMock:
        """Obtain the appropriate type of mock, supporting both sync and async modes."""
        if isinstance(self.writer, BaseSyncWriter):
            return Mock
        return AsyncMock

    @pytest.fixture()
    def autopatch(self, monkeypatch: pytest.MonkeyPatch):
        """Create a simple function, supporting patching both sync/async writer functions with appropriate mocks.

        This returned function takes in the name of the function to patch, and returns the mock object.
        This mock object will either be Mock, or AsyncMock instance, depending on whether we're in async or sync mode.
        """
        if isinstance(self.writer, SyncWriter):
            patch_path = "mcproto.protocol.base_io.BaseSyncWriter"
            mock_type = Mock
        else:
            patch_path = "mcproto.protocol.base_io.BaseAsyncWriter"
            mock_type = AsyncMock

        def autopatch(function_name: str) -> Mock | AsyncMock:
            mock_f = mock_type()
            monkeypatch.setattr(f"{patch_path}.{function_name}", mock_f)
            return mock_f

        return autopatch

    @pytest.fixture()
    def write_mock(self, monkeypatch: pytest.MonkeyPatch):
        """Monkeypatch the write function with a mock which is returned."""
        mock_f = WriteFunctionMock() if isinstance(self.writer, BaseSyncWriter) else WriteFunctionAsyncMock()
        monkeypatch.setattr(self.writer.__class__, "write", mock_f)
        return mock_f

    @pytest.mark.parametrize(
        ("fmt", "value", "expected_bytes"),
        [
            (StructFormat.UBYTE, 0, [0]),
            (StructFormat.UBYTE, 15, [15]),
            (StructFormat.UBYTE, 255, [255]),
            (StructFormat.BYTE, 0, [0]),
            (StructFormat.BYTE, 15, [15]),
            (StructFormat.BYTE, 127, [127]),
            (StructFormat.BYTE, -20, [to_twos_complement(-20, bits=8)]),
            (StructFormat.BYTE, -128, [to_twos_complement(-128, bits=8)]),
        ],
    )
    def test_write_value(
        self,
        fmt: INT_FORMATS_TYPE,
        value: Any,
        expected_bytes: list[int],
        write_mock: WriteFunctionMock,
    ):
        """Test writing values sends expected bytes."""
        self.writer.write_value(fmt, value)
        write_mock.assert_has_data(bytearray(expected_bytes))

    @pytest.mark.parametrize(
        ("fmt", "value"),
        [
            (StructFormat.UBYTE, -1),
            (StructFormat.UBYTE, 256),
            (StructFormat.BYTE, -129),
            (StructFormat.BYTE, 128),
        ],
    )
    def test_write_value_out_of_range(
        self,
        fmt: INT_FORMATS_TYPE,
        value: Any,
    ):
        """Test writing out of range values for the given format raises :exc:`struct.error`."""
        with pytest.raises(struct.error):
            self.writer.write_value(fmt, value)

    @pytest.mark.parametrize(
        ("number", "expected_bytes"),
        [
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
        ],
    )
    def test_write_varuint(self, number: int, expected_bytes: list[int], write_mock: WriteFunctionMock):
        """Test writing varuints results in correct bytes."""
        self.writer._write_varuint(number)  # pyright: ignore[reportPrivateUsage]
        write_mock.assert_has_data(bytearray(expected_bytes))

    @pytest.mark.parametrize(
        ("write_value", "max_bits"),
        [
            (-1, 128),
            (-1, 1),
            (2**16, 16),
            (2**32, 32),
        ],
    )
    def test_write_varuint_out_of_range(self, write_value: int, max_bits: int):
        """Test writing out of range varuints raises :exc:`ValueError`."""
        with pytest.raises(ValueError):
            self.writer._write_varuint(write_value, max_bits=max_bits)  # pyright: ignore[reportPrivateUsage]

    @pytest.mark.parametrize(
        ("number", "expected_bytes"),
        [(127, [127]), (16384, [128, 128, 1]), (-128, [128, 255, 255, 255, 15]), (-16383, [129, 128, 255, 255, 15])],
    )
    def test_write_varint(self, number: int, expected_bytes: list[int], write_mock: WriteFunctionMock):
        """Test writing varints results in correct bytes."""
        self.writer.write_varint(number)
        write_mock.assert_has_data(bytearray(expected_bytes))

    @pytest.mark.parametrize(
        ("number", "expected_bytes"),
        [
            (127, [127]),
            (16384, [128, 128, 1]),
            (-128, [128, 255, 255, 255, 255, 255, 255, 255, 255, 1]),
            (-16383, [129, 128, 255, 255, 255, 255, 255, 255, 255, 1]),
        ],
    )
    def test_write_varlong(self, number: int, expected_bytes: list[int], write_mock: WriteFunctionMock):
        """Test writing varlongs results in correct bytes."""
        self.writer.write_varlong(number)
        write_mock.assert_has_data(bytearray(expected_bytes))

    @pytest.mark.parametrize(
        ("data", "expected_bytes"),
        [
            (b"", [0]),
            (b"\x01", [1, 1]),
            (b"hello\0world", [11, 104, 101, 108, 108, 111, 0, 119, 111, 114, 108, 100]),
            (b"\x01\x02\x03four\x05", [8, 1, 2, 3, 102, 111, 117, 114, 5]),
        ],
    )
    def test_write_bytearray(self, data: bytes, expected_bytes: list[int], write_mock: WriteFunctionMock):
        """Test writing ASCII string results in correct bytes."""
        self.writer.write_bytearray(data)
        write_mock.assert_has_data(bytearray(expected_bytes))

    @pytest.mark.parametrize(
        ("string", "expected_bytes"),
        [
            ("test", [*list(map(ord, "test")), 0]),
            ("a" * 100, [*list(map(ord, "a" * 100)), 0]),
            ("", [0]),
        ],
    )
    def test_write_ascii(self, string: str, expected_bytes: list[int], write_mock: WriteFunctionMock):
        """Test writing ASCII string results in correct bytes."""
        self.writer.write_ascii(string)
        write_mock.assert_has_data(bytearray(expected_bytes))

    @pytest.mark.parametrize(
        ("string", "expected_bytes"),
        [
            ("test", [len("test"), *list(map(ord, "test"))]),
            ("a" * 100, [len("a" * 100), *list(map(ord, "a" * 100))]),
            ("", [0]),
            ("नमस्ते", [18] + [int(x) for x in "नमस्ते".encode()]),
        ],
    )
    def test_write_utf(self, string: str, expected_bytes: list[int], write_mock: WriteFunctionMock):
        """Test writing UTF string results in correct bytes."""
        self.writer.write_utf(string)
        write_mock.assert_has_data(bytearray(expected_bytes))

    @pytest.mark.skipif(platform.system() == "Windows", reason="environment variable limit on Windows")
    def test_write_utf_limit(self, write_mock: WriteFunctionMock):
        """Test writing a UTF string too big raises a :exc:`ValueError`."""
        with pytest.raises(ValueError, match="Maximum character limit for writing strings is 32767 characters."):
            self.writer.write_utf("a" * (32768))

    def test_write_optional_true(self, method_mock: Mock | AsyncMock, write_mock: WriteFunctionMock):
        """Test writing non-``None`` value writes ``True`` and runs the writer function."""
        mock_v = Mock()
        mock_f = method_mock()
        self.writer.write_optional(mock_v, mock_f)
        mock_f.assert_called_once_with(mock_v)
        write_mock.assert_has_data(bytearray([1]))

    def test_write_optional_false(self, method_mock: Mock | AsyncMock, write_mock: WriteFunctionMock):
        """Test writing ``None`` value should write ``False`` and skip running the writer function."""
        mock_f = method_mock()
        self.writer.write_optional(None, mock_f)
        mock_f.assert_not_called()
        write_mock.assert_has_data(bytearray([0]))


class ReaderTests(abc, generic[T_READER]):
    """Collection of tests for both sync and async versions of the reader."""

    reader: T_READER

    @classmethod
    @abstractmethod
    def setup_class(cls):
        """Initialize reader instance to be tested."""
        ...

    @pytest.fixture()
    def method_mock(self) -> Mock | AsyncMock:
        """Obtain the appropriate type of mock, supporting both sync and async modes."""
        if isinstance(self.reader, BaseSyncReader):
            return Mock
        return AsyncMock

    @pytest.fixture()
    def autopatch(self, monkeypatch: pytest.MonkeyPatch):
        """Create a simple function, supporting patching both sync/async reader functions with appropriate mocks.

        This returned function takes in the name of the function to patch, and returns the mock object.
        This mock object will either be Mock, or AsyncMock instance, depending on whether we're in async or sync mode.
        """
        if isinstance(self.reader, SyncReader):
            patch_path = "mcproto.protocol.base_io.BaseSyncReader"
            mock_type = Mock
        else:
            patch_path = "mcproto.protocol.base_io.BaseAsyncReader"
            mock_type = AsyncMock

        def autopatch(function_name: str) -> Mock | AsyncMock:
            mock_f = mock_type()
            monkeypatch.setattr(f"{patch_path}.{function_name}", mock_f)
            return mock_f

        return autopatch

    @pytest.fixture()
    def read_mock(self, monkeypatch: pytest.MonkeyPatch):
        """Monkeypatch the read function with a mock which is returned."""
        mock_f = ReadFunctionMock() if isinstance(self.reader, SyncReader) else ReadFunctionAsyncMock()
        monkeypatch.setattr(self.reader.__class__, "read", mock_f)
        yield mock_f
        # Run this assertion after the test, to ensure that all specified data
        # to be read, actually was read
        mock_f.assert_read_everything()

    @pytest.mark.parametrize(
        ("fmt", "read_bytes", "expected_value"),
        [
            (StructFormat.UBYTE, [0], 0),
            (StructFormat.UBYTE, [10], 10),
            (StructFormat.UBYTE, [255], 255),
            (StructFormat.BYTE, [0], 0),
            (StructFormat.BYTE, [20], 20),
            (StructFormat.BYTE, [127], 127),
            (StructFormat.BYTE, [to_twos_complement(-20, bits=8)], -20),
            (StructFormat.BYTE, [to_twos_complement(-128, bits=8)], -128),
        ],
    )
    def test_read_value(
        self,
        fmt: INT_FORMATS_TYPE,
        read_bytes: list[int],
        expected_value: Any,
        read_mock: ReadFunctionMock,
    ):
        """Test reading bytes gets expected value."""
        read_mock.combined_data = bytearray(read_bytes)
        assert self.reader.read_value(fmt) == expected_value

    @pytest.mark.parametrize(
        ("read_bytes", "expected_value"),
        [
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
        ],
    )
    def test_read_varuint(self, read_bytes: list[int], expected_value: int, read_mock: ReadFunctionMock):
        """Test reading varuint bytes results in correct values."""
        read_mock.combined_data = bytearray(read_bytes)
        assert self.reader._read_varuint() == expected_value  # pyright: ignore[reportPrivateUsage]

    @pytest.mark.parametrize(
        ("read_bytes", "max_bits"),
        [
            ([128, 128, 4], 16),
            ([128, 128, 128, 128, 16], 32),
        ],
    )
    def test_read_varuint_out_of_range(self, read_bytes: list[int], max_bits: int, read_mock: ReadFunctionMock):
        """Test reading out-of-range varuints raises :exc:`IOError`."""
        read_mock.combined_data = bytearray(read_bytes)
        with pytest.raises(IOError):
            self.reader._read_varuint(max_bits=max_bits)  # pyright: ignore[reportPrivateUsage]

    @pytest.mark.parametrize(
        ("read_bytes", "expected_value"),
        [([127], 127), ([128, 128, 1], 16384), ([128, 255, 255, 255, 15], -128), ([129, 128, 255, 255, 15], -16383)],
    )
    def test_read_varint(self, read_bytes: list[int], expected_value: int, read_mock: ReadFunctionMock):
        """Test reading varuint bytes results in correct values."""
        read_mock.combined_data = bytearray(read_bytes)
        assert self.reader.read_varint() == expected_value

    @pytest.mark.parametrize(
        ("read_bytes", "expected_value"),
        [
            ([127], 127),
            ([128, 128, 1], 16384),
            ([128, 255, 255, 255, 255, 255, 255, 255, 255, 1], -128),
            ([129, 128, 255, 255, 255, 255, 255, 255, 255, 1], -16383),
        ],
    )
    def test_read_varlong(self, read_bytes: list[int], expected_value: int, read_mock: ReadFunctionMock):
        """Test reading varuint bytes results in correct values."""
        read_mock.combined_data = bytearray(read_bytes)
        assert self.reader.read_varlong() == expected_value

    @pytest.mark.parametrize(
        ("read_bytes", "expected_bytes"),
        [
            ([0], b""),
            ([1, 1], b"\x01"),
            ([11, 104, 101, 108, 108, 111, 0, 119, 111, 114, 108, 100], b"hello\0world"),
            ([8, 1, 2, 3, 102, 111, 117, 114, 5], b"\x01\x02\x03four\x05"),
        ],
    )
    def test_read_bytearray(self, read_bytes: list[int], expected_bytes: bytes, read_mock: ReadFunctionMock):
        """Test reading ASCII string results in correct bytes."""
        read_mock.combined_data = bytearray(read_bytes)
        assert self.reader.read_bytearray() == expected_bytes

    @pytest.mark.parametrize(
        ("read_bytes", "expected_string"),
        [
            ([*list(map(ord, "test")), 0], "test"),
            ([*list(map(ord, "a" * 100)), 0], "a" * 100),
            ([0], ""),
        ],
    )
    def test_read_ascii(self, read_bytes: list[int], expected_string: str, read_mock: ReadFunctionMock):
        """Test reading ASCII string results in correct bytes."""
        read_mock.combined_data = bytearray(read_bytes)
        assert self.reader.read_ascii() == expected_string

    @pytest.mark.parametrize(
        ("read_bytes", "expected_string"),
        [
            ([len("test"), *list(map(ord, "test"))], "test"),
            ([len("a" * 100), *list(map(ord, "a" * 100))], "a" * 100),
            ([0], ""),
            ([18] + [int(x) for x in "नमस्ते".encode()], "नमस्ते"),
        ],
    )
    def test_read_utf(self, read_bytes: list[int], expected_string: str, read_mock: ReadFunctionMock):
        """Test reading UTF string results in correct values."""
        read_mock.combined_data = bytearray(read_bytes)
        assert self.reader.read_utf() == expected_string

    @pytest.mark.skipif(platform.system() == "Windows", reason="environment variable limit on Windows")
    @pytest.mark.parametrize(
        ("read_bytes"),
        [
            [253, 255, 7],
            [128, 128, 2, *list(map(ord, "a" * 32768))],
        ],
        # Temporary workaround.
        # https://github.com/pytest-dev/pytest/issues/6881#issuecomment-596381626
        ids=["a", "b"],
    )
    def test_read_utf_limit(self, read_bytes: list[int], read_mock: ReadFunctionMock):
        """Test reading a UTF string too big raises an IOError."""
        read_mock.combined_data = bytearray(read_bytes)
        with pytest.raises(IOError):
            self.reader.read_utf()

    def test_read_optional_true(self, method_mock: Mock | AsyncMock, read_mock: ReadFunctionMock):
        """Test reading optional runs reader function when first bool is ``True``."""
        mock_f = method_mock()
        read_mock.combined_data = bytearray([1])
        self.reader.read_optional(mock_f)
        mock_f.assert_called_once_with()

    def test_read_optional_false(self, method_mock: Mock | AsyncMock, read_mock: ReadFunctionMock):
        """Test reading optional doesn't run reader function when first bool is ``False``."""
        mock_f = method_mock()
        read_mock.combined_data = bytearray([0])
        self.reader.read_optional(mock_f)
        mock_f.assert_not_called()


# endregion
# region: Concrete test classes


# Pytest workaround, see the comment above in a similar location.
if sys.version_info > (3, 9) or TYPE_CHECKING:
    writer_tests_cls = WriterTests
    reader_tests_cls = ReaderTests
else:
    # boy this is cursed
    writer_tests_cls = {SyncWriter: WriterTests, AsyncWriter: WriterTests}
    reader_tests_cls = {SyncReader: ReaderTests, AsyncReader: ReaderTests}


class TestBaseSyncWriter(writer_tests_cls[SyncWriter]):
    """Tests for individual write methods implemented in :class:`~mcproto.protocol.base_io.BaseSyncWriter`."""

    @override
    @classmethod
    def setup_class(cls):
        cls.writer = SyncWriter()


class TestBaseSyncReader(reader_tests_cls[SyncReader]):
    """Tests for individual write methods implemented in :class:`~mcproto.protocol.base_io.BaseSyncReader`."""

    @override
    @classmethod
    def setup_class(cls):
        cls.reader = SyncReader()


class TestBaseAsyncWriter(writer_tests_cls[AsyncWriter]):
    """Tests for individual write methods implemented in :class:`~mcproto.protocol.base_io.BaseSyncReader`."""

    @override
    @classmethod
    def setup_class(cls):
        cls.writer = WrappedAsyncWriter()  # type: ignore


class TestBaseAsyncReader(reader_tests_cls[AsyncReader]):
    """Tests for individual write methods implemented in :class:`~mcproto.protocol.base_io.BaseSyncReader`."""

    @override
    @classmethod
    def setup_class(cls):
        cls.reader = WrappedAsyncReader()  # type: ignore


# endregion
