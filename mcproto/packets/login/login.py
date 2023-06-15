from __future__ import annotations

from typing import ClassVar, Optional, final

from typing_extensions import Self

from mcproto.buffer import Buffer
from mcproto.packets.packet import ClientBoundPacket, GameState, ServerBoundPacket
from mcproto.types.chat import ChatMessage
from mcproto.types.uuid import UUID

__all__ = [
    "LoginStart",
    "LoginEncryptionRequest",
    "LoginEncryptionResponse",
    "LoginSuccess",
    "LoginDisconnect",
    "LoginPluginRequest",
    "LoginPluginResponse",
    "LoginSetCompression",
]


@final
class LoginStart(ServerBoundPacket):
    """Packet from client asking to start login process. (Client -> Server)"""

    __slots__ = ("username", "uuid")

    PACKET_ID: ClassVar[int] = 0x00
    GAME_STATE: ClassVar[GameState] = GameState.LOGIN

    def __init__(self, *, username: str, uuid: UUID | None):
        """
        :param username: Username of the client who sent the request.
        :param uuid: UUID of the player logging in (if the player doesn't have a UUID, this can be ``None``)
        """
        self.username = username
        self.uuid = uuid

    def serialize(self) -> Buffer:
        buf = Buffer()
        buf.write_utf(self.username)
        buf.write_optional(self.uuid, lambda id: buf.extend(id.serialize()))
        return buf

    @classmethod
    def deserialize(cls, buf: Buffer, /) -> Self:
        username = buf.read_utf()
        uuid = buf.read_optional(lambda: UUID.deserialize(buf))
        return cls(username=username, uuid=uuid)


@final
class LoginEncryptionRequest(ClientBoundPacket):
    """Used by the server to ask the client to encrypt the login process. (Server -> Client)"""

    __slots__ = ("server_id", "public_key", "verify_token")

    PACKET_ID: ClassVar[int] = 0x01
    GAME_STATE: ClassVar[GameState] = GameState.LOGIN

    def __init__(self, *, server_id: str | None = None, public_key: bytes, verify_token: bytes):
        """
        :param server_id: Empty on minecraft versions 1.7.X and higher (20 random chars pre 1.7).
        :param public_key: Server's public key.
        :param verify_token: Sequence of random bytes generated by server for verification.
        """
        if server_id is None:
            server_id = " " * 20

        self.server_id = server_id
        self.public_key = public_key
        self.verify_token = verify_token

    def serialize(self) -> Buffer:
        buf = Buffer()
        buf.write_utf(self.server_id)
        buf.write_bytearray(self.public_key)
        buf.write_bytearray(self.verify_token)
        return buf

    @classmethod
    def deserialize(cls, buf: Buffer, /) -> Self:
        server_id = buf.read_utf()
        public_key = buf.read_bytearray()
        verify_token = buf.read_bytearray()
        return cls(server_id=server_id, public_key=public_key, verify_token=verify_token)


@final
class LoginEncryptionResponse(ServerBoundPacket):
    """Response from the client to LoginEncryptionRequest. (Client -> Server)"""

    __slots__ = ("shared_secret", "verify_token")

    PACKET_ID: ClassVar[int] = 0x01
    GAME_STATE: ClassVar[GameState] = GameState.LOGIN

    def __init__(self, *, shared_secret: bytes, verify_token: bytes):
        """
        :param shared_secret: Shared secret value, encrypted with server's public key.
        :param verify_token: Verify token value, encrypted with same public key.
        """
        self.shared_secret = shared_secret
        self.verify_token = verify_token

    def serialize(self) -> Buffer:
        buf = Buffer()
        buf.write_bytearray(self.shared_secret)
        buf.write_bytearray(self.verify_token)
        return buf

    @classmethod
    def deserialize(cls, buf: Buffer, /) -> Self:
        shared_secret = buf.read_bytearray()
        verify_token = buf.read_bytearray()
        return cls(shared_secret=shared_secret, verify_token=verify_token)


@final
class LoginSuccess(ClientBoundPacket):
    """Sent by the server to denote a successful login. (Server -> Client)"""

    __slots__ = ("uuid", "username")

    PACKET_ID: ClassVar[int] = 0x02
    GAME_STATE: ClassVar[GameState] = GameState.LOGIN

    def __init__(self, uuid: UUID, username: str):
        """
        :param uuid: The UUID of the connecting player/client.
        :param username: The username of the connecting player/client.
        """
        self.uuid = uuid
        self.username = username

    def serialize(self) -> Buffer:
        buf = Buffer()
        buf.extend(self.uuid.serialize())
        buf.write_utf(self.username)
        return buf

    @classmethod
    def deserialize(cls, buf: Buffer, /) -> Self:
        uuid = UUID.deserialize(buf)
        username = buf.read_utf()
        return cls(uuid, username)


@final
class LoginDisconnect(ClientBoundPacket):
    """Sent by the server to kick a player while in the login state. (Server -> Client)"""

    __slots__ = ("reason",)

    PACKET_ID: ClassVar[int] = 0x00
    GAME_STATE: ClassVar[GameState] = GameState.LOGIN

    def __init__(self, reason: ChatMessage):
        """
        :param reason: The reason for disconnection (kick).
        """
        self.reason = reason

    def serialize(self) -> Buffer:
        return self.reason.serialize()

    @classmethod
    def deserialize(cls, buf: Buffer, /) -> Self:
        reason = ChatMessage.deserialize(buf)
        return cls(reason)


@final
class LoginPluginRequest(ClientBoundPacket):
    """Sent by the server to implement a custom handshaking flow. (Server -> Client)"""

    __slots__ = ("message_id", "channel", "data")

    PACKET_ID: ClassVar[int] = 0x04
    GAME_STATE: ClassVar[GameState] = GameState.LOGIN

    def __init__(self, message_id: int, channel: str, data: bytes):
        """
        :param message_id: Message id, generated by the server, should be unique to the connection.
        :param channel: Channel identifier, name of the plugin channel used to send data.
        :param data: Data that is to be sent.
        """
        self.message_id = message_id
        self.channel = channel
        self.data = data

    def serialize(self) -> Buffer:
        buf = Buffer()
        buf.write_varint(self.message_id)
        buf.write_utf(self.channel)
        buf.write(self.data)
        return buf

    @classmethod
    def deserialize(cls, buf: Buffer, /) -> Self:
        message_id = buf.read_varint()
        channel = buf.read_utf()
        data = buf.read(buf.remaining)  # All of the remaining data in the buffer
        return cls(message_id, channel, data)


@final
class LoginPluginResponse(ServerBoundPacket):
    """Response to LoginPluginRequest from client. (Client -> Server)"""

    __slots__ = ("message_id", "data")

    PACKET_ID: ClassVar[int] = 0x02
    GAME_STATE: ClassVar[GameState] = GameState.LOGIN

    def __init__(self, message_id: int, data: Optional[bytes]):
        """
        :param message_id: Message id, generated by the server, should be unique to the connection.
        :param data: Optional response data, present if client understood request.
        """
        self.message_id = message_id
        self.data = data

    def serialize(self) -> Buffer:
        buf = Buffer()
        buf.write_varint(self.message_id)
        buf.write_optional(self.data, buf.write)
        return buf

    @classmethod
    def deserialize(cls, buf: Buffer, /) -> Self:
        message_id = buf.read_varint()
        data = buf.read_optional(lambda: buf.read(buf.remaining))
        return cls(message_id, data)


@final
class LoginSetCompression(ClientBoundPacket):
    """Sent by the server to specify whether to use compression on future packets or not (Server -> Client).

    Note that this packet is optional, and if not set, the compression will not be enabled at all."""

    __slots__ = ("threshold",)

    PACKET_ID: ClassVar[int] = 0x03
    GAME_STATE: ClassVar[GameState] = GameState.LOGIN

    def __init__(self, threshold: int):
        """
        :param threshold:
            Maximum size of a packet before it is compressed. All packets smaller than this will remain uncompressed.
            To disable compression completely, threshold can be set to -1.
        """
        self.threshold = threshold

    def serialize(self) -> Buffer:
        buf = Buffer()
        buf.write_varint(self.threshold)
        return buf

    @classmethod
    def deserialize(cls, buf: Buffer, /) -> Self:
        threshold = buf.read_varint()
        return cls(threshold)
