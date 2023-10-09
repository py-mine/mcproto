from __future__ import annotations

import httpx

from mcproto.auth.account import Account
from mcproto.connection import TCPAsyncConnection
from mcproto.encryption import encrypt_token_and_secret, generate_shared_secret
from mcproto.exceptions import InvalidGameStateError, UnexpectedPacketError
from mcproto.multiplayer import compute_server_hash, join_request
from mcproto.packets.handshaking.handshake import Handshake, NextState
from mcproto.packets.interactions import async_read_packet, async_write_packet
from mcproto.packets.login.login import (
    LoginDisconnect,
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


class Client:
    """Class representing the client, capable of connecting to the server.

    This class holds the logic for all client interactions/flows, is aware if the current
    game state, packet compression, encryption, etc.
    """

    __slots__ = (
        "host",
        "port",
        "httpx_client",
        "account",
        "conn",
        "protocol_version",
        "game_state",
        "packet_compression_threshold",
    )

    def __init__(  # noqa: PLR0913
        self,
        host: str,
        port: int,
        httpx_client: httpx.AsyncClient,
        account: Account,
        conn: TCPAsyncConnection,
        protocol_version: int,
        game_state: GameState | None = None,
        packet_compression_threshold: int = -1,
    ) -> None:
        self.host = host
        self.port = port
        self.httpx_client = httpx_client
        self.account = account
        self.conn = conn
        self.protocol_version = protocol_version
        self.game_state = game_state
        self.packet_compression_threshold = packet_compression_threshold

    async def _write_packet(self, packet: ServerBoundPacket) -> None:
        """Write a packet to the connection.

        This sends the given ``packet`` to the server, respecting the current configuration
        (compression threshold, encryption, ...)
        """
        await async_write_packet(self.conn, packet, compression_threshold=self.packet_compression_threshold)

    async def _read_packet(self) -> ClientBoundPacket:
        """Read a packet from the connection.

        This receives a packet from the server, resolving it based on the current configuration
        (using a packet map for current game state, compression threshold, encryption, ...)
        """
        if self.game_state is None:
            raise InvalidGameStateError(
                "Receiving packet failed",
                expected=tuple(state for state in GameState.__members__.values()),  # Any non-None game state
                found=self.game_state,  # None
            )

        packet_map = generate_packet_map(PacketDirection.CLIENTBOUND, self.game_state)
        return await async_read_packet(
            self.conn,
            packet_map,
            compression_threshold=self.packet_compression_threshold,
        )

    async def _handshake(self, next_state: NextState) -> None:
        """Send the handshake packet, transitioning us to ``next_state``."""
        if self.game_state is not None:
            raise InvalidGameStateError("Sending handshake failed", expected=None, found=self.game_state)

        packet = Handshake(
            protocol_version=self.protocol_version,
            server_address=self.host,
            server_port=self.port,
            next_state=next_state,
        )
        await self._write_packet(packet)
        self.game_state = GameState.STATUS if next_state is NextState.STATUS else GameState.LOGIN

    async def ping(self, payload: int) -> PingPong:
        """Ping the server."""
        if self.game_state is None:
            await self._handshake(NextState.STATUS)

        if self.game_state is not GameState.STATUS:
            raise InvalidGameStateError("Requesting ping failed", expected=GameState.STATUS, found=self.game_state)

        packet = PingPong(payload)
        await self._write_packet(packet)

        recv_packet = await self._read_packet()
        if not isinstance(recv_packet, PingPong):
            raise UnexpectedPacketError("Receiving ping response failed", expected=PingPong, found=recv_packet)

        return recv_packet

    async def status(self) -> StatusResponse:
        """Obtain status data from the server.

        This goes through the status flow, obtaining back a status response packet.
        """
        if self.game_state is None:
            await self._handshake(NextState.STATUS)

        if self.game_state is not GameState.STATUS:
            raise InvalidGameStateError("Requesting status failed", expected=GameState.STATUS, found=self.game_state)

        packet = StatusRequest()
        await self._write_packet(packet)

        recv_packet = await self._read_packet()
        if not isinstance(recv_packet, StatusResponse):
            raise UnexpectedPacketError("Receiving status response failed", expected=StatusResponse, found=recv_packet)

        return recv_packet

    async def _handle_encryption_request(self, packet: LoginEncryptionRequest) -> None:
        """Handle receiving the :class:`mcproto.packets.login.login.LoginEncryptionRequest` packet.

        This will create a new shared secret for symmetric AES/CFB8 encryption, send it back to
        the server encrypted using it's public key from the ``LoginEncryptionRequest`` packet.

        This allows the server to safely receive our randomly generated shared secret, and as
        both sides now have the same encryption key, encryption is enabled. All further
        communication will be encrypted.
        """
        shared_secret = generate_shared_secret()

        # If the server isn't in offline mode (has server_id of "-"), contact the session server API.
        if packet.server_id != "-":
            server_hash = compute_server_hash(packet.server_id, shared_secret, packet.public_key)
            await join_request(self.httpx_client, self.account, server_hash)

        encrypted_token, encrypted_secret = encrypt_token_and_secret(
            packet.public_key,
            packet.verify_token,
            shared_secret,
        )

        response_packet = LoginEncryptionResponse(shared_secret=encrypted_secret, verify_token=encrypted_token)
        await self._write_packet(response_packet)

        self.conn.enable_encryption(shared_secret)

    async def login(self) -> None:
        """Go through the."""
        if self.game_state is None:
            await self._handshake(NextState.LOGIN)

        if self.game_state is not GameState.LOGIN:
            raise InvalidGameStateError("Login flow failed", expected=GameState.LOGIN, found=self.game_state)

        start_packet = LoginStart(username=self.account.username, uuid=self.account.uuid)
        await self._write_packet(start_packet)

        # Keep reading new packets until we get LoginSuccess from server
        # we don't really know the receive order here, as some servers use non-standard ordering
        # (i.e. sending set compression before encryption request)
        while not isinstance((recv_packet := await self._read_packet()), LoginSuccess):
            if isinstance(recv_packet, LoginDisconnect):
                raise UnexpectedPacketError(
                    f"Login failed, server sent disconnect! Reason: {recv_packet.reason!r}",
                    expected=(LoginEncryptionRequest, LoginSetCompression, LoginSuccess),
                    found=recv_packet,
                )

            if isinstance(recv_packet, LoginSetCompression):
                self.packet_compression_threshold = recv_packet.threshold
                continue

            if isinstance(recv_packet, LoginEncryptionRequest):
                await self._handle_encryption_request(recv_packet)
                continue

            raise UnexpectedPacketError(
                "Login failed, server sent unexpected packet",
                expected=(LoginEncryptionRequest, LoginSetCompression, LoginSuccess),
                found=recv_packet,
            )

        # We now know the received packet is LoginSuccess, do some sanity checks for it's validity
        if recv_packet.username != self.account.username:
            raise IOError(
                "Received LoginSuccess packet that didn't match request account username!"
                f" request_username={self.account.username!r}, received_username={recv_packet.username!r}"
            )
        if recv_packet.uuid != self.account.uuid:
            raise IOError(
                "Received LoginSuccess packet that didn't match request account uuid!"
                f" request_uuid={self.account.uuid!r}, received_uuid={recv_packet.uuid!r}"
            )

        # Transition to PLAY state
        self.game_state = GameState.PLAY

        # Wait for Login (play) packet now. It could take a while for some servers to
        # transition to the play state, but we can be certain the server won't send any
        # other packets before this Login one.
        recv_packet = await self._read_packet()
        # TODO: Mcproto doesn't yet contain PLAY game state packets
