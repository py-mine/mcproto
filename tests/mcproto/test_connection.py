from __future__ import annotations

import asyncio
import errno
import socket
from unittest.mock import MagicMock

import pytest

from mcproto.connection import TCPAsyncConnection, TCPSyncConnection
from tests.helpers import CustomMockMixin
from tests.mcproto.protocol.helpers import ReadFunctionAsyncMock, ReadFunctionMock, WriteFunctionMock


class MockSocket(CustomMockMixin, MagicMock):
    spec_set = socket.socket

    def __init__(self, *args, read_data: bytearray | None = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.mock_add_spec(["_recv", "_send", "_closed"])
        self._recv = ReadFunctionMock(combined_data=read_data)
        self._send = WriteFunctionMock()
        self._closed = False

    def send(self, data: bytearray) -> None:
        if self._closed:
            raise OSError(errno.EBADF, "Bad file descriptor")
        return self._send(data)

    def recv(self, length: int) -> bytearray:
        if self._closed:
            raise OSError(errno.EBADF, "Bad file descriptor")
        return self._recv(length)

    def close(self) -> None:
        self._closed = True

    def shutdown(self, __how: int, /) -> None:
        pass


class MockStreamWriter(CustomMockMixin, MagicMock):
    spec_set = asyncio.StreamWriter

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mock_add_spec(["_white", "_closed"])
        self._write = WriteFunctionMock()
        self._closed = False

    def write(self, data: bytearray) -> None:
        if self._closed:
            raise OSError(errno.EBADF, "Bad file descriptor")
        return self._write(data)

    def close(self) -> None:
        self._closed = True


class MockStreamReader(CustomMockMixin, MagicMock):
    spec_set = asyncio.StreamReader

    def __init__(self, *args, read_data: bytearray | None = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.mock_add_spec(["_read"])
        self._read = ReadFunctionAsyncMock(combined_data=read_data)

    def read(self, length: int) -> bytearray:
        return self._read(length)


class TestTCPSyncConnection:
    def make_connection(self, read_data: bytearray | None = None) -> TCPSyncConnection[MockSocket]:
        if read_data is not None:
            read_data = read_data.copy()

        return TCPSyncConnection(MockSocket(read_data=read_data))

    def test_read(self):
        data = bytearray("hello", "utf-8")
        conn = self.make_connection(data)

        out = conn.read(5)

        assert out == data
        conn.socket._recv.assert_read_everything()

    def test_read_more_data_than_sent(self):
        data = bytearray("test", "utf-8")
        conn = self.make_connection(data)

        with pytest.raises(IOError):
            conn.read(10)

    def test_encrypted_read(self):
        # The encryption is done with AES/CFB8 stream cipher
        key = bytearray.fromhex("f71e3033d4c0fc6aadee4417831b5c3e")
        plaintext_data = bytearray.fromhex("1077656c6c2068656c6c6f207468657265")
        encrypted_data = bytearray.fromhex("1ee5262f2df60b7262bed1ee27a3056184")

        conn = self.make_connection(encrypted_data)
        conn.enable_encryption(key)

        assert conn.read(17) == plaintext_data

    def test_write(self):
        data = bytearray("hello", "utf-8")
        conn = self.make_connection()

        conn.write(data)

        conn.socket._send.assert_has_data(data)

    def test_encrypted_write(self):
        # The encryption is done with AES/CFB8 stream cipher
        key = bytearray.fromhex("f71e3033d4c0fc6aadee4417831b5c3e")
        plaintext_data = bytearray.fromhex("1077656c6c2068656c6c6f207468657265")
        encrypted_data = bytearray.fromhex("1ee5262f2df60b7262bed1ee27a3056184")

        conn = self.make_connection()
        conn.enable_encryption(key)

        conn.write(plaintext_data)
        conn.socket._send.assert_has_data(encrypted_data)

    def test_socket_close(self):
        conn = self.make_connection()

        conn.close()
        assert conn.socket._closed is True

    def test_socket_close_contextmanager(self):
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
    def make_connection(
        self,
        read_data: bytearray | None = None,
    ) -> TCPAsyncConnection[MockStreamReader, MockStreamWriter]:
        if read_data is not None:
            read_data = read_data.copy()

        return TCPAsyncConnection(MockStreamReader(read_data=read_data), MockStreamWriter(), 3)

    async def test_read(self):
        data = bytearray("hello", "utf-8")
        conn = self.make_connection(data)

        out = await conn.read(5)

        assert out == data
        conn.reader._read.assert_read_everything()

    async def test_read_more_data_than_sent(self):
        data = bytearray("test", "utf-8")
        conn = self.make_connection(data)

        with pytest.raises(IOError):
            await conn.read(10)

    async def test_write(self):
        data = bytearray("hello", "utf-8")
        conn = self.make_connection()

        await conn.write(data)

        conn.writer._write.assert_has_data(data)

    async def test_socket_close(self):
        conn = self.make_connection()

        await conn.close()
        assert conn.writer._closed is True

    async def test_socket_close_contextmanager(self):
        conn = self.make_connection()

        async with conn as _:
            pass

        # Internal writer gets closed once context manager is exited
        assert conn.writer._closed is True

        # Can't reopen closed connection
        with pytest.raises(OSError):
            async with conn as _:
                pass
