from __future__ import annotations

import asyncio
import errno
import socket
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

import asyncio_dgram
from typing_extensions import ParamSpec, Self

from mcproto.protocol.base_io import BaseAsyncReader, BaseAsyncWriter, BaseSyncReader, BaseSyncWriter

__all__ = [
    "AsyncConnection",
    "SyncConnection",
    "TCPAsyncConnection",
    "TCPSyncConnection",
    "UDPAsyncConnection",
    "UDPSyncConnection",
]

P = ParamSpec("P")
R = TypeVar("R")
T_SOCK = TypeVar("T_SOCK", bound=socket.socket)
T_STREAMREADER = TypeVar("T_STREAMREADER", bound=asyncio.StreamReader)
T_STREAMWRITER = TypeVar("T_STREAMWRITER", bound=asyncio.StreamWriter)
T_DATAGRAM_CLIENT = TypeVar("T_DATAGRAM_CLIENT", bound=asyncio_dgram.aio.DatagramClient)


class SyncConnection(BaseSyncReader, BaseSyncWriter, ABC):
    """Base class for all classes handling synchronous connections."""

    __slots__ = ("closed",)

    def __init__(self):
        self.closed = False

    @classmethod
    @abstractmethod
    def make_client(cls, address: tuple[str, int], timeout: float) -> Self:
        """Construct a client connection (Client -> Server) to given server ``address``.

        :param address: Address of the server to connection to.
        :param timeout:
            Amount of seconds to wait for the connection to be established.
            If connection can't be established within this time, :exc:`TimeoutError` will be raised.
            This timeout is then also used for any further data receiving.
        """
        raise NotImplementedError

    @abstractmethod
    def _close(self) -> None:
        """Close the underlying connection."""
        raise NotImplementedError

    def close(self) -> None:
        """Close the connection (it cannot be used after this)."""
        self._close()
        self.closed = True

    def __enter__(self) -> Self:
        if self.closed:
            raise IOError("Connection already closed.")
        return self

    def __exit__(self, *a, **kw) -> None:
        self.close()


class AsyncConnection(BaseAsyncReader, BaseAsyncWriter, ABC):
    """Base class for all classes handling asynchronous connections."""

    __slots__ = ("closed",)

    def __init__(self):
        self.closed = False

    @classmethod
    @abstractmethod
    async def make_client(cls, address: tuple[str, int], timeout: float) -> Self:
        """Construct a client connection (Client -> Server) to given server ``address``.

        :param address: Address of the server to connection to.
        :param timeout:
            Amount of seconds to wait for the connection to be established.
            If connection can't be established within this time, :exc:`TimeoutError` will be raised.
            This timeout is then also used for any further data receiving.
        """
        raise NotImplementedError

    @abstractmethod
    async def _close(self) -> None:
        """Close the underlying connection."""
        raise NotImplementedError

    async def close(self) -> None:
        """Close the connection (it cannot be used after this)."""
        await self._close()
        self.closed = True

    async def __aenter__(self) -> Self:
        if self.closed:
            raise IOError("Connection already closed.")
        return self

    async def __aexit__(self, *a, **kw) -> None:
        await self.close()


class TCPSyncConnection(SyncConnection, Generic[T_SOCK]):
    """Synchronous connection using a TCP :class:`~socket.socket`."""

    __slots__ = ("socket",)

    def __init__(self, socket: T_SOCK):
        super().__init__()
        self.socket = socket

    @classmethod
    def make_client(cls, address: tuple[str, int], timeout: float) -> Self:
        """Construct a client connection (Client -> Server) to given server ``address``.

        :param address: Address of the server to connection to.
        :param timeout:
            Amount of seconds to wait for the connection to be established.
            If connection can't be established within this time, :exc:`TimeoutError` will be raised.
            This timeout is then also used for any further data receiving.
        """
        sock = socket.create_connection(address, timeout=timeout)
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        return cls(sock)

    def read(self, length: int) -> bytearray:
        """Receive data sent through the connection.

        :param length:
            Amount of bytes to be received. If the requested amount can't be received
            (server didn't send that much data/server didn't send any data), an :exc:`IOError`
            will be raised.
        """
        result = bytearray()
        while len(result) < length:
            new = self.socket.recv(length - len(result))
            if len(new) == 0:
                # No information at all
                if len(result) == 0:
                    raise IOError("Server did not respond with any information.")
                # Only sent a few bytes, but we requested more
                raise IOError(
                    f"Server stopped responding (got {len(result)} bytes, but expected {length} bytes)."
                    f" Partial obtained data: {result!r}"
                )
            result.extend(new)

        return result

    def write(self, data: bytes) -> None:
        """Send given ``data`` over the connection."""
        self.socket.send(data)

    def _close(self) -> None:
        """Close the underlying connection."""
        # Gracefully end the connection first (shutdown), informing the other side
        # we're disconnecting, and waiting for them to disconnect cleanly (TCP FIN)
        try:
            self.socket.shutdown(socket.SHUT_RDWR)
        except OSError as exc:
            if exc.errno != errno.ENOTCONN:
                raise

        self.socket.close()


class TCPAsyncConnection(AsyncConnection, Generic[T_STREAMREADER, T_STREAMWRITER]):
    """Asynchronous TCP connection using :class:`~asyncio.StreamWriter` and :class:`~asyncio.StreamReader`."""

    __slots__ = ("reader", "writer", "timeout")

    def __init__(self, reader: T_STREAMREADER, writer: T_STREAMWRITER, timeout: float):
        super().__init__()
        self.reader = reader
        self.writer = writer
        self.timeout = timeout

    @classmethod
    async def make_client(cls, address: tuple[str, int], timeout: float) -> Self:
        """Construct a client connection (Client -> Server) to given server ``address``.

        :param address: Address of the server to connection to.
        :param timeout:
            Amount of seconds to wait for the connection to be established.
            If connection can't be established within this time, :exc:`TimeoutError` will be raised.
            This timeout is then also used for any further data receiving.
        """
        conn = asyncio.open_connection(address[0], address[1])
        reader, writer = await asyncio.wait_for(conn, timeout=timeout)
        return cls(reader, writer, timeout)

    async def read(self, length: int) -> bytearray:
        """Receive data sent through the connection.

        :param length:
            Amount of bytes to be received. If the requested amount can't be received
            (server didn't send that much data/server didn't send any data), an :exc:`IOError`
            will be raised.
        """
        result = bytearray()
        while len(result) < length:
            new = await asyncio.wait_for(self.reader.read(length - len(result)), timeout=self.timeout)
            if len(new) == 0:
                # No information at all
                if len(result) == 0:
                    raise IOError("Server did not respond with any information.")
                # Only sent a few bytes, but we requested more
                raise IOError(
                    f"Server stopped responding (got {len(result)} bytes, but expected {length} bytes)."
                    f" Partial obtained data: {result!r}"
                )
            result.extend(new)

        return result

    async def write(self, data: bytes) -> None:
        """Send given ``data`` over the connection."""
        self.writer.write(data)

    async def _close(self) -> None:
        """Close the underlying connection."""
        # Close automatically performs a graceful TCP connection shutdown too
        self.writer.close()

    @property
    def socket(self) -> socket.socket:
        """Obtain the underlying socket behind the :class:`~asyncio.Transport`."""
        return self.writer.transport._sock  # type: ignore


class UDPSyncConnection(SyncConnection, Generic[T_SOCK]):
    """Synchronous connection using a UDP :class:`~socket.socket`."""

    __slots__ = ("socket", "address")

    BUFFER_SIZE = 65535

    def __init__(self, socket: T_SOCK, address: tuple[str, int]):
        super().__init__()
        self.socket = socket
        self.address = address

    @classmethod
    def make_client(cls, address: tuple[str, int], timeout: float) -> Self:
        """Construct a client connection (Client -> Server) to given server ``address``.

        :param address: Address of the server to connection to.
        :param timeout:
            Amount of seconds to wait for the connection to be established.
            If connection can't be established within this time, :exc:`TimeoutError` will be raised.
            This timeout is then also used for any further data receiving.
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(timeout)
        return cls(sock, address)

    def read(self, length: int | None = None) -> bytearray:
        """Receive data sent through the connection.

        :param length:
            For UDP connections, ``length`` parameter is ignored and not required.
            Instead, UDP connections always read exactly :attr:`.BUFFER_SIZE` bytes.

            If the requested amount can't be received (server didn't send that much
            data/server didn't send any data), an :exc:`IOError` will be raised.
        """
        result = bytearray()
        while len(result) == 0:
            received_data, server_addr = self.socket.recvfrom(self.BUFFER_SIZE)
            result.extend(received_data)
        return result

    def write(self, data: bytes) -> None:
        """Send given ``data`` over the connection."""
        self.socket.sendto(data, self.address)

    def _close(self) -> None:
        """Close the underlying connection."""
        self.socket.close()


class UDPAsyncConnection(AsyncConnection, Generic[T_DATAGRAM_CLIENT]):
    """Asynchronous UDP connection using :class:`~asyncio_dgram.DatagramClient`."""

    __slots__ = ("stream", "timeout")

    def __init__(self, stream: T_DATAGRAM_CLIENT, timeout: float):
        super().__init__()
        self.stream = stream
        self.timeout = timeout

    @classmethod
    async def make_client(cls, address: tuple[str, int], timeout: float) -> Self:
        """Construct a client connection (Client -> Server) to given server ``address``.

        :param address: Address of the server to connection to.
        :param timeout:
            Amount of seconds to wait for the connection to be established.
            If connection can't be established within this time, :exc:`TimeoutError` will be raised.
            This timeout is then also used for any further data receiving.
        """
        conn = asyncio_dgram.connect(address)
        stream = await asyncio.wait_for(conn, timeout=timeout)
        return cls(stream, timeout)

    async def read(self, length: int | None = None) -> bytearray:
        """Receive data sent through the connection.

        :param length:
            For UDP connections, ``length`` parameter is ignored and not required.

            If the requested amount can't be received (server didn't send that much
            data/server didn't send any data), an :exc:`IOError` will be raised.
        """
        result = bytearray()
        while len(result) == 0:
            received_data, server_addr = await asyncio.wait_for(self.stream.recv(), timeout=self.timeout)
            result.extend(received_data)
        return result

    async def write(self, data: bytes) -> None:
        """Send given ``data`` over the connection."""
        await self.stream.send(data)

    async def _close(self) -> None:
        """Close the underlying connection."""
        self.stream.close()
