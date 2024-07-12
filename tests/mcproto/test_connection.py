from __future__ import annotations

import asyncio
import errno
import socket
from unittest.mock import MagicMock

import pytest
from typing_extensions import override

from mcproto.connection import TCPAsyncConnection, TCPSyncConnection
from tests.helpers import CustomMockMixin
from tests.mcproto.protocol.helpers import ReadFunctionAsyncMock, ReadFunctionMock, WriteFunctionMock


class MockSocket(CustomMockMixin, MagicMock):
    """Mock version of a socket (synchronous), using our mocked writer and reader methods.

    See :class:`tests.mcproto.protocol.helpers.ReadFunctionMock` and
    :class:`tests.mcproto.protocol.helpers.WriteFunctionMock`.
    """

    spec_set = socket.socket

    def __init__(self, *args, read_data: bytearray | None = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.mock_add_spec(["_recv", "_send", "_closed"])
        self._recv = ReadFunctionMock(combined_data=read_data)
        self._send = WriteFunctionMock()
        self._closed = False

    @override
    def send(self, data: bytearray) -> None:
        """Mock version of send method, raising :exc:`OSError` if the socket was closed."""
        if self._closed:
            raise OSError(errno.EBADF, "Bad file descriptor")
        return self._send(data)

    @override
    def recv(self, length: int) -> bytearray:
        """Mock version of recv method, raising :exc:`OSError` if the socket was closed."""
        if self._closed:
            raise OSError(errno.EBADF, "Bad file descriptor")
        return self._recv(length)

    @override
    def close(self) -> None:
        """Mock version of close method, setting :attr:`_closed` bool flag."""
        self._closed = True

    @override
    def shutdown(self, __how: int, /) -> None:
        """Mock version of shutdown, without any real implementation."""


class MockStreamWriter(CustomMockMixin, MagicMock):
    """Mock version of :class:`asyncio.StreamWriter` using our mocked writer method."""

    spec_set = asyncio.StreamWriter

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mock_add_spec(["_white", "_closed"])
        self._write = WriteFunctionMock()
        self._closed = False

    @override
    def write(self, data: bytearray) -> None:
        """Mock version of write method, raising :exc:`OSError` if the writer was closed."""
        if self._closed:
            raise OSError(errno.EBADF, "Bad file descriptor")
        return self._write(data)

    @override
    def close(self) -> None:
        """Mock version of close method, setting :attr:`_closed` bool flag."""
        self._closed = True


class MockStreamReader(CustomMockMixin, MagicMock):
    """Mock version of :class:`asyncio.StreamReader` using our mocked reader method."""

    spec_set = asyncio.StreamReader

    def __init__(self, *args, read_data: bytearray | None = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.mock_add_spec(["_read"])
        self._read = ReadFunctionAsyncMock(combined_data=read_data)

    @override
    def read(self, length: int) -> bytearray:
        """Mock version of read, using the mocked read method."""
        return self._read(length)


class TestTCPSyncConnection:
    """Collection of tests for the synchronous TCP connection class."""

    def make_connection(self, read_data: bytearray | None = None) -> TCPSyncConnection[MockSocket]:
        """Create a new connection class using the :class:`MockSocket` class."""
        if read_data is not None:
            read_data = read_data.copy()

        return TCPSyncConnection(MockSocket(read_data=read_data))

    def test_read(self):
        """Test reading data returns the original (input) data."""
        data = bytearray("hello", "utf-8")
        conn = self.make_connection(data)

        out = conn.read(5)

        assert out == data
        conn.socket._recv.assert_read_everything()

    def test_read_more_data_than_sent(self):
        """Test reading more data than available raises :exc:`IOError`."""
        data = bytearray("test", "utf-8")
        conn = self.make_connection(data)

        with pytest.raises(IOError):
            _ = conn.read(10)

    def test_encrypted_read(self):
        """Test reading encrypted data with enabled encryption properly decrypts the data."""
        # The encryption is done with AES/CFB8 stream cipher
        key = bytearray.fromhex("f71e3033d4c0fc6aadee4417831b5c3e")
        plaintext_data = bytearray.fromhex("1077656c6c2068656c6c6f207468657265")
        encrypted_data = bytearray.fromhex("1ee5262f2df60b7262bed1ee27a3056184")

        conn = self.make_connection(encrypted_data)
        conn.enable_encryption(key)

        assert conn.read(17) == plaintext_data

    def test_write(self):
        """Test writing data sends that original (unmodified) data."""
        data = bytearray("hello", "utf-8")
        conn = self.make_connection()

        conn.write(data)

        conn.socket._send.assert_has_data(data)

    def test_encrypted_write(self):
        """Test writing plaintext data with enabled encryption encrypts the data before sending."""
        # The encryption is done with AES/CFB8 stream cipher
        key = bytearray.fromhex("f71e3033d4c0fc6aadee4417831b5c3e")
        plaintext_data = bytearray.fromhex("1077656c6c2068656c6c6f207468657265")
        encrypted_data = bytearray.fromhex("1ee5262f2df60b7262bed1ee27a3056184")

        conn = self.make_connection()
        conn.enable_encryption(key)

        conn.write(plaintext_data)
        conn.socket._send.assert_has_data(encrypted_data)

    def test_socket_close(self):
        """Test close method closes the underlying socket."""
        conn = self.make_connection()

        conn.close()
        assert conn.socket._closed is True

    def test_socket_close_contextmanager(self):
        """Test using connection as context manager closes the underlying socket afterwards."""
        conn = self.make_connection()

        with conn as _:
            pass

        # Internal socket gets closed once context manager is exited
        assert conn.socket._closed is True

        # Can't reopen closed connection
        with pytest.raises(OSError):  # noqa: SIM117
            with conn as _:
                pass


class TestTCPAsyncConnection:
    """Collection of tests for the asynchronous TCP connection class."""

    def make_connection(
        self,
        read_data: bytearray | None = None,
    ) -> TCPAsyncConnection[MockStreamReader, MockStreamWriter]:
        """Create a new connection class using the :class:`MockStreamReader` and :class:`MockStreamWriter` classes."""
        if read_data is not None:
            read_data = read_data.copy()

        return TCPAsyncConnection(MockStreamReader(read_data=read_data), MockStreamWriter(), 3)

    async def test_read(self):
        """Test reading data returns the original (input) data."""
        data = bytearray("hello", "utf-8")
        conn = self.make_connection(data)

        out = await conn.read(5)

        assert out == data
        conn.reader._read.assert_read_everything()

    async def test_read_more_data_than_sent(self):
        """Test reading more data than available raises :exc:`IOError`."""
        data = bytearray("test", "utf-8")
        conn = self.make_connection(data)

        with pytest.raises(IOError):
            _ = await conn.read(10)

    async def test_encrypted_read(self):
        """Test reading encrypted data with enabled encryption properly decrypts the data."""
        # The encryption is done with AES/CFB8 stream cipher
        key = bytearray.fromhex("f71e3033d4c0fc6aadee4417831b5c3e")
        plaintext_data = bytearray.fromhex("1077656c6c2068656c6c6f207468657265")
        encrypted_data = bytearray.fromhex("1ee5262f2df60b7262bed1ee27a3056184")

        conn = self.make_connection(encrypted_data)
        conn.enable_encryption(key)

        assert await conn.read(17) == plaintext_data

    async def test_write(self):
        """Test writing data sends that original (unmodified) data."""
        data = bytearray("hello", "utf-8")
        conn = self.make_connection()

        await conn.write(data)

        conn.writer._write.assert_has_data(data)

    async def test_encrypted_write(self):
        """Test writing plaintext data with enabled encryption encrypts the data before sending."""
        # The encryption is done with AES/CFB8 stream cipher
        key = bytearray.fromhex("f71e3033d4c0fc6aadee4417831b5c3e")
        plaintext_data = bytearray.fromhex("1077656c6c2068656c6c6f207468657265")
        encrypted_data = bytearray.fromhex("1ee5262f2df60b7262bed1ee27a3056184")

        conn = self.make_connection()
        conn.enable_encryption(key)

        await conn.write(plaintext_data)
        conn.writer._write.assert_has_data(encrypted_data)

    async def test_socket_close(self):
        """Test close method closes the underlying socket."""
        conn = self.make_connection()

        await conn.close()
        assert conn.writer._closed is True

    async def test_socket_close_contextmanager(self):
        """Test using connection as context manager closes the underlying socket afterwards."""
        conn = self.make_connection()

        async with conn as _:
            pass

        # Internal writer gets closed once context manager is exited
        assert conn.writer._closed is True

        # Can't reopen closed connection
        with pytest.raises(OSError):
            async with conn as _:
                pass
