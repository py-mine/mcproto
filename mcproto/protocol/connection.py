from __future__ import annotations

import asyncio
import socket
from typing import TYPE_CHECKING, Tuple, TypeVar

from mcproto.protocol.abc import BaseAsyncReader, BaseAsyncWriter, BaseSyncReader, BaseSyncWriter

if TYPE_CHECKING:
    from typing_extensions import ParamSpec

    P = ParamSpec("P")

R = TypeVar("R")


class TCPSyncConnection(BaseSyncReader, BaseSyncWriter):
    def __init__(self, address: Tuple[str, int], timeout: float):
        self.address = address
        self.timeout = timeout
        self.socket = socket.create_connection(address, timeout=timeout)
        self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

    def read(self, length: int) -> bytearray:
        result = bytearray()
        while len(result) < length:
            new = self.socket.recv(length - len(result))
            if len(new) == 0:
                if len(result) == 0:
                    raise IOError("Server did not respond with any information.")
                raise IOError(
                    f"Server stopped responding (got {len(result)} bytes, but expected {length} bytes)."
                    f" Partial obtained data: {result!r}"
                )
            result.extend(new)

        return result

    def write(self, data: bytes) -> None:
        self.socket.send(data)

    def close(self) -> None:
        self.socket.close()


class TCPAsyncConnection(BaseAsyncReader, BaseAsyncWriter):
    def __init__(self, address: Tuple[str, int], timeout: float):
        self._connected = False
        self.address = address
        self.timeout: float = timeout
        # These will be set in async connect() function
        self.reader: asyncio.StreamReader = None  # type: ignore
        self.writer: asyncio.StreamWriter = None  # type: ignore

    async def connect(self) -> None:
        conn = asyncio.open_connection(self.address[0], self.address[1])
        self.reader, self.writer = await asyncio.wait_for(conn, timeout=self.timeout)
        self._connected = True

    async def read(self, length: int) -> bytearray:
        if self._connected is False:
            await self.connect()

        result = bytearray()
        while len(result) < length:
            new = await asyncio.wait_for(self.reader.read(length - len(result)), timeout=self.timeout)
            if len(new) == 0:
                if len(result) == 0:
                    raise IOError("Server did not respond with any information.")
                raise IOError(
                    f"Server stopped responding (got {len(result)} bytes, but expected {length} bytes)."
                    f" Partial obtained data: {result!r}"
                )
            result.extend(new)

        return result

    def close(self) -> None:
        self.writer.close()
        self._connected = False
