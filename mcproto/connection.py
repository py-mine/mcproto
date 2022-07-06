from __future__ import annotations

import asyncio
import socket
from typing import Generic, Optional, TYPE_CHECKING, TypeVar

import asyncio_dgram

from mcproto.protocol.base_io import BaseAsyncReader, BaseAsyncWriter, BaseSyncReader, BaseSyncWriter

if TYPE_CHECKING:
    from typing_extensions import ParamSpec, Self

    P = ParamSpec("P")

R = TypeVar("R")
T_SOCK = TypeVar("T_SOCK", bound=socket.socket)
T_STREAMREADER = TypeVar("T_STREAMREADER", bound=asyncio.StreamReader)
T_STREAMWRITER = TypeVar("T_STREAMWRITER", bound=asyncio.StreamWriter)
T_DATAGRAM_CLIENT = TypeVar("T_DATAGRAM_CLIENT", bound=asyncio_dgram.aio.DatagramClient)


class TCPSyncConnection(BaseSyncReader, BaseSyncWriter, Generic[T_SOCK]):
    def __init__(self, socket: T_SOCK):
        self.socket = socket

    @classmethod
    def make_client(cls, address: tuple[str, int], timeout: float) -> Self:
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
    async def make_client(cls, address: tuple[str, int], timeout: float) -> Self:
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

    async def write(self, data: bytes) -> None:
        self.writer.write(data)

    def close(self) -> None:
        self.writer.close()


class UDPSyncConnection(BaseSyncReader, BaseSyncWriter, Generic[T_SOCK]):
    BUFFER_SIZE = 65535

    def __init__(self, socket: T_SOCK, address: tuple[str, int]):
        self.socket = socket
        self.address = address

    @classmethod
    def make_client(cls, address: tuple[str, int], timeout: float) -> Self:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(timeout)
        return cls(sock, address)

    def read(self, length: Optional[int] = None) -> bytearray:
        result = bytearray()
        while len(result) == 0:
            received_data, server_addr = self.socket.recvfrom(self.BUFFER_SIZE)
            result.extend(received_data)
        return result

    def write(self, data: bytes) -> None:
        self.socket.sendto(data, self.address)

    def close(self) -> None:
        self.socket.close()


class UDPAsyncConnection(BaseAsyncReader, BaseAsyncWriter, Generic[T_DATAGRAM_CLIENT]):
    def __init__(self, stream: T_DATAGRAM_CLIENT, timeout: float):
        self.stream = stream
        self.timeout = timeout

    @classmethod
    async def make_client(cls, address: tuple[str, int], timeout: float) -> Self:
        conn = asyncio_dgram.connect(address)
        stream = await asyncio.wait_for(conn, timeout=timeout)
        return cls(stream, timeout)

    async def read(self, length: Optional[int] = None) -> bytearray:
        result = bytearray()
        while len(result) == 0:
            received_data, server_addr = await asyncio.wait_for(self.stream.recv(), timeout=self.timeout)
            result.extend(received_data)
        return result

    async def write(self, data: bytes) -> None:
        await self.stream.send(data)

    def close(self) -> None:
        self.stream.close()
