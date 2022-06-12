from __future__ import annotations

import asyncio
import socket
from typing import Generic, TYPE_CHECKING, Tuple, TypeVar

from mcproto.protocol.abc import BaseAsyncReader, BaseAsyncWriter, BaseSyncReader, BaseSyncWriter

if TYPE_CHECKING:
    from typing_extensions import ParamSpec, Self

    P = ParamSpec("P")

R = TypeVar("R")
T_SOCK = TypeVar("T_SOCK", bound=socket.socket)
T_STREAMREADER = TypeVar("T_STREAMREADER", bound=asyncio.StreamReader)
T_STREAMWRITER = TypeVar("T_STREAMWRITER", bound=asyncio.StreamWriter)


class TCPSyncConnection(BaseSyncReader, BaseSyncWriter, Generic[T_SOCK]):
    def __init__(self, socket: T_SOCK):
        self.socket = socket

    @classmethod
    def make_client(cls, address: Tuple[str, int], timeout: float) -> Self:
        sock = socket.create_connection(address, timeout=timeout)
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        return cls(sock)

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


class TCPAsyncConnection(BaseAsyncReader, BaseAsyncWriter, Generic[T_STREAMREADER, T_STREAMWRITER]):
    def __init__(self, reader: T_STREAMREADER, writer: T_STREAMWRITER, timeout: float):
        self.reader = reader
        self.writer = writer
        self.timeout = timeout

    @classmethod
    async def make_client(cls, address: Tuple[str, int], timeout: float) -> Self:
        conn = asyncio.open_connection(address[0], address[1])
        reader, writer = await asyncio.wait_for(conn, timeout=timeout)
        return cls(reader, writer, timeout)

    async def read(self, length: int) -> bytearray:
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
