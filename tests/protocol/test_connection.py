from __future__ import annotations

import asyncio
import socket
from typing import Optional
from unittest.mock import MagicMock

import pytest

from mcproto.protocol.connection import TCPAsyncConnection, TCPSyncConnection
from tests.protocol.helpers import ReadFunctionAsyncMock, ReadFunctionMock, WriteFunctionMock


class MockSocket(MagicMock):
    spec_set = socket.socket

    def __init__(self, *args, read_data: Optional[bytearray] = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.recv = ReadFunctionMock(combined_data=read_data)
        self.send = WriteFunctionMock()


class MockStreamWriter(MagicMock):
    spec_set = asyncio.StreamWriter

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.write = WriteFunctionMock()


class MockStreamReader(MagicMock):
    spec_set = asyncio.StreamReader

    def __init__(self, *args, read_data: Optional[bytearray] = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.read = ReadFunctionAsyncMock(combined_data=read_data)


class TestTCPSycnConnection:
    def make_connection(self, read_data: Optional[bytearray] = None) -> TCPSyncConnection[MockSocket]:
        if read_data is not None:
            read_data = read_data.copy()

        return TCPSyncConnection(MockSocket(read_data=read_data))

    def test_read(self):
        data = bytearray("hello", "utf-8")
        conn = self.make_connection(data)

        out = conn.read(5)

        conn.socket.recv.assert_read_everything()
        assert out == data

    def test_read_more_data_than_sent(self):
        data = bytearray("test", "utf-8")
        conn = self.make_connection(data)

        with pytest.raises(IOError):
            conn.read(10)

    def test_write(self):
        data = bytearray("hello", "utf-8")
        conn = self.make_connection()

        conn.write(data)

        conn.socket.send.assert_has_data(data)


class TestTCPAsycnConnection:
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

        conn.reader.read.assert_read_everything()
        assert out == data

    async def test_read_more_data_than_sent(self):
        data = bytearray("test", "utf-8")
        conn = self.make_connection(data)

        with pytest.raises(IOError):
            await conn.read(10)

    async def test_write(self):
        data = bytearray("hello", "utf-8")
        conn = self.make_connection()

        await conn.write(data)

        conn.writer.write.assert_has_data(data)
