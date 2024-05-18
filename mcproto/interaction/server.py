from __future__ import annotations

import asyncio
from typing import NoReturn
from uuid import uuid4

import httpx
from typing_extensions import Self

from mcproto.connection import TCPAsyncConnection
from mcproto.encryption import decrypt_token_and_secret, generate_rsa_key, generate_verify_token
from mcproto.interaction.exceptions import InvalidVerifyTokenError, UnexpectedPacketError
from mcproto.multiplayer import compute_server_hash, join_check
from mcproto.packets.handshaking.handshake import Handshake, NextState
from mcproto.packets.interactions import async_read_packet, async_write_packet
from mcproto.packets.login.login import (
    LoginEncryptionRequest,
    LoginEncryptionResponse,
    LoginSetCompression,
    LoginStart,
    LoginSuccess,
)
from mcproto.packets.packet import ClientBoundPacket, GameState, PacketDirection, ServerBoundPacket
from mcproto.packets.packet_map import generate_packet_map
from mcproto.packets.status.ping import PingPong
from mcproto.packets.status.status import StatusRequest, StatusResponse
from mcproto.types.uuid import UUID as McUUID  # noqa: N811 # UUID isn't a constant


class ConnectedClient:
    """Class holding data about a client connected to the server.

    This class is aware of the current gamestate for this client, compression, encryption, ...
    """

    __slots__ = ("conn", "game_state", "compression_threshold", "username", "uuid")

    def __init__(
        self,
        conn: TCPAsyncConnection,
        *,
        game_state: GameState,
        compression_threshold: int = -1,
    ):
        self.conn = conn
        self.game_state = game_state
        self.compression_threshold = compression_threshold

        # Manually set by the server, once LoginStart is received
        self.username: str
        self.uuid: McUUID

    @classmethod
    def new_connection(
        cls,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
        *,
        compression_threshold: int = -1,
        timeout: int = 3,
    ) -> Self:
        """Create a new client from the received `reader` and `writer`."""
        conn = TCPAsyncConnection(reader, writer, timeout=timeout)
        return cls(conn, game_state=GameState.HANDSHAKING, compression_threshold=compression_threshold)

    async def close(self) -> None:
        """Close the connection with this client."""
        await self.conn.close()

    async def write_packet(self, packet: ClientBoundPacket) -> None:
        """Write a packet to the client connection.

        This sends the given ``packet`` to the client, respecting the current configuration
        (compression threshold, encryption, ...)
        """
        await async_write_packet(self.conn, packet, compression_threshold=self.compression_threshold)

    async def read_packet(self) -> ServerBoundPacket:
        """Read a packet from the client connection.

        This receives a packet from the client, resolving it based on the current configuration
        (using a packet map for current game state, compression threshold, encryption, ...)
        """
        packet_map = generate_packet_map(PacketDirection.SERVERBOUND, self.game_state)
        return await async_read_packet(self.conn, packet_map, compression_threshold=self.compression_threshold)

    @property
    def ip(self) -> str:
        """Obtain the IP address of the client."""
        return self.conn.writer.get_extra_info("peername")[0]


class Server:
    """Class representing the server, capable of communication with multiple clients.

    This class holds the logic for all server interactions/flows, and is capable to
    process received client requests and act accordingly.
    """

    __slots__ = (
        "host",
        "port",
        "httpx_client",
        "enable_encryption",
        "online",
        "compression_threshold",
        "prevent_proxy_connections",
    )

    def __init__(
        self,
        host: str,
        port: int,
        *,
        httpx_client: httpx.AsyncClient,
        enable_encryption: bool,
        online: bool,
        compression_threshold: int = -1,
        prevent_proxy_connections: bool = False,
    ):
        if online and not enable_encryption:
            raise ValueError("Can't use online mode without encryption")

        self.host = host
        self.port = port
        self.httpx_client = httpx_client
        self.enable_encryption = enable_encryption
        self.online = online
        self.compression_threshold = compression_threshold
        self.prevent_proxy_connections = prevent_proxy_connections

    async def start(self) -> NoReturn:
        """Start the server, and run it forever."""
        server = await asyncio.start_server(self.handle_client, self.host, self.port)
        async with server:
            await server.serve_forever()

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        """Handle incoming connection from a client."""
        client = ConnectedClient.new_connection(reader, writer)

        try:
            await self.handle_handshaking_gamestate(client)

            if client.game_state is GameState.STATUS:
                await self.handle_status_gamestate(client)
            elif client.game_state is GameState.LOGIN:
                await self.handle_login_gamestate(client)
            else:
                raise  # never
        finally:
            await client.close()

    async def handle_handshaking_gamestate(self, client: ConnectedClient) -> None:
        """Handle client entering the handshaking gamestate (initial state)."""
        handshake_packet = await client.read_packet()
        if not isinstance(handshake_packet, Handshake):
            raise UnexpectedPacketError("Receiving handshake failed", expected=Handshake, found=handshake_packet)

        if handshake_packet.next_state is NextState.LOGIN:
            client.game_state = GameState.LOGIN
        elif handshake_packet.next_state is NextState.STATUS:
            client.game_state = GameState.STATUS
        else:
            raise  # never

    async def handle_status_gamestate(self, client: ConnectedClient) -> None:
        """Handle client entering the status state.

        The client is now expected to either send a status request, or a ping, or both
        with status request being the first packet.

        If the first requested packet wasn't a status request, it can't be requested anymore!
        However ping can be requested as many times as the client wants.
        """
        recv_packet = await client.read_packet()
        if isinstance(recv_packet, StatusRequest):
            packet = StatusResponse(self.status)
            await client.write_packet(packet)

            try:
                recv_packet = await client.read_packet()
            # If we can't read any more packets here, the client has probably
            # ended the connection, do the same
            except IOError:
                return

        while True:
            if isinstance(recv_packet, PingPong):
                packet = PingPong(recv_packet.payload)
                await client.write_packet(packet)
            else:
                raise UnexpectedPacketError("Status flow failed", expected=PingPong, found=recv_packet)

            try:
                recv_packet = await client.read_packet()
            # If we can't read any more packets here, the client has probably
            # ended the connection, do the same
            except IOError:
                return

    async def _handle_encryption_request(self, client: ConnectedClient) -> None:
        """Handle sending the :class:`~mcproto.packets.login.login.LoginEncryptionRequest` packet.

        This will generate an RSA keypair, sending the public key to the client, which will use it
        to encrypt the shared secret value for symmetric AES/CFB8 encryption generated by the client.

        This allows the client to safely send a randomly generated shared secret, and as both
        sides will now have the same encryption key, encryption is enabled. All further
        communication will be encrypted.
        """
        rsa_key = generate_rsa_key()
        verify_token = generate_verify_token()
        server_id = "" if self.online else "-"

        packet = LoginEncryptionRequest(
            server_id=server_id,
            public_key=rsa_key.public_key(),
            verify_token=verify_token,
        )
        await client.write_packet(packet)

        recv_packet = await client.read_packet()
        if not isinstance(recv_packet, LoginEncryptionResponse):
            raise UnexpectedPacketError("Login flow failed", expected=LoginEncryptionResponse, found=recv_packet)

        decrypted_token, decrypted_secret = decrypt_token_and_secret(
            rsa_key,
            recv_packet.verify_token,
            recv_packet.shared_secret,
        )
        if decrypted_token != verify_token:
            raise InvalidVerifyTokenError(verify_token, decrypted_token)

        client.conn.enable_encryption(decrypted_secret)

        if self.online:
            client_ip = client.ip if self.prevent_proxy_connections else None
            server_hash = compute_server_hash(server_id, decrypted_secret, rsa_key.public_key())
            ack_data = await join_check(self.httpx_client, client.username, server_hash, client_ip)

            client.uuid = McUUID(ack_data["id"])
            client.username = ack_data["name"]

    async def handle_login_gamestate(self, client: ConnectedClient) -> None:
        """Handle client entering the login state."""
        login_start_packet = await client.read_packet()
        if not isinstance(login_start_packet, LoginStart):
            raise UnexpectedPacketError("Login flow failed", expected=LoginStart, found=login_start_packet)

        client.username = login_start_packet.username
        client.uuid = login_start_packet.uuid or McUUID(str(uuid4()))

        if self.enable_encryption:
            await self._handle_encryption_request(client)

        if self.compression_threshold >= 0:
            packet = LoginSetCompression(self.compression_threshold)
            await client.write_packet(packet)

        packet = LoginSuccess(client.uuid, client.username)
        await client.write_packet(packet)

        # Transition to play
        return await self.handle_play_gamestate(client)

    async def handle_play_gamestate(self, client: ConnectedClient) -> None:
        """Handle client entering the play state."""
        raise NotImplementedError("Play state packets aren't implemented yet")
        while True:
            await client.read_packet()

    @property
    def status(self) -> dict[str, object]:
        """Return the server info (used in `~mcproto.packets.status.status.StatusResponse`)."""
        return {
            "version": {"name": "1.20.2", "protocol": 764},
            "enforcesSecureChat": True,
            "description": {"text": "A Vanilla Minecraft Server powered by Mcproto"},
            "players": {"max": 20, "online": 0},
        }
