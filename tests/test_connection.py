from __future__ import annotations

import asyncio
import errno
import socket
from typing import Optional
from unittest.mock import MagicMock

import pytest

from mcproto.connection import TCPAsyncConnection, TCPSyncConnection
from tests.helpers import CustomMockMixin
from tests.protocol.helpers import ReadFunctionAsyncMock, ReadFunctionMock, WriteFunctionMock


class MockSocket(CustomMockMixin, MagicMock):
    spec_set = socket.socket

    def __init__(self, *args, read_data: Optional[bytearray] = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
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


class MockStreamWriter(CustomMockMixin, MagicMock):
    spec_set = asyncio.StreamWriter

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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

    def __init__(self, *args, read_data: Optional[bytearray] = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._read = ReadFunctionAsyncMock(combined_data=read_data)

    def read(self, length: int) -> bytearray:
        return self._read(length)


class TestTCPSyncConnection:
    def make_connection(self, read_data: Optional[bytearray] = None) -> TCPSyncConnection[MockSocket]:
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

    def test_write(self):
        data = bytearray("hello", "utf-8")
        conn = self.make_connection()

        conn.write(data)

        conn.socket._send.assert_has_data(data)

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
        read_data: Optional[bytearray] = None,
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
