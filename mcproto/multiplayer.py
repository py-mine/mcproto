from __future__ import annotations

import hashlib
from enum import Enum
from typing import TypedDict

import httpx
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from typing_extensions import Self

from mcproto.auth.account import Account
from mcproto.types.uuid import UUID as McUUID  # noqa: N811 # not a constant

__all__ = [
    "SessionServerError",
    "SessionServerErrorType",
    "join_request",
    "join_check",
    "compute_server_hash",
]

SESSION_SERVER_URL = "https://sessionserver.mojang.com"


class SessionServerErrorType(str, Enum):
    BANNED_FROM_MULTIPLAYER = "User with has been banned from multiplayer."
    XBOX_MULTIPLAYER_DISABLED = "User's Xbox profile has multiplayer disabled."
    UNKNOWN = "This is an unknown error."

    @classmethod
    def from_status_error(cls, code: int, err_msg: str | None) -> Self:
        if code == 403:
            if err_msg == "InsufficientPrivilegesException":
                return cls.XBOX_MULTIPLAYER_DISABLED
            if err_msg == "UserBannedException":
                return cls.BANNED_FROM_MULTIPLAYER
        return cls.UNKNOWN


class SessionServerError(Exception):
    def __init__(self, exc: httpx.HTTPStatusError):
        self.status_error = exc
        self.code = exc.response.status_code
        self.url = exc.request.url

        data = exc.response.json()
        self.err_msg: str | None = data.get("error")
        self.err_type = SessionServerErrorType.from_status_error(self.code, self.err_msg)

        super().__init__(self.msg)

    @property
    def msg(self) -> str:
        msg_parts = []
        msg_parts.append(f"HTTP {self.code} from {self.url}:")
        msg_parts.append(f"type={self.err_type.name!r}")

        if self.err_type is not SessionServerErrorType.UNKNOWN:
            msg_parts.append(f"details={self.err_type.value!r}")
        elif self.err_msg is not None:
            msg_parts.append(f"msg={self.err_msg!r}")

        return " ".join(msg_parts)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.msg})"


class JoinAcknowledgeProperty(TypedDict):
    name: str
    value: str
    signature: str


class JoinAcknowledgeData(TypedDict):
    id: str
    name: str
    properties: list[JoinAcknowledgeProperty]


def compute_server_hash(server_id: str, shared_secret: bytes, server_public_key: RSAPublicKey) -> str:
    """Compute a hash to be sent as 'serverId' field to Mojang session server.

    This function is used for :func:`join_request` and :func:`join_check` functions, which require
    this hash value.

    This SHA1 hash is computed based on the ``server_id``, ``server_public_key`` and ``shared_secret``.
    Together, these values ensure that there can't be any middle-man listening in after encryption is
    established.

    This is because a middle man/proxy who would want to listed into the encrypted communication would
    need to know the encryption key (``shared_secret``). A proxy can capture this key, as the client
    sends it over to the server in :class:`~mcproto.packets.login.login.LoginEncryptionResponse` packet,
    however it is sent encrypted. The client performs this encryption with a public key, which it got
    from the server, in :class:`mcproto.packets.login.login.LoginEncryptionRequest` packet.

    That mans that for a proxy to be able to actually obtain this shared secret value, it would need to
    be able to capture the encryption response, and decrypt the shared secret value. That means it would
    need to send a spoofed version of the encryption request packet, with the server's public key
    replaced by one that the proxy owns a private key for. This will work, and the proxy could indeed
    decrypt the sent shared secret now. All it would need to do now is send this shared secret to the
    server. That's easy, just re-encrypt it with the server's original public key, and send it in a
    custom encryption request!

    So then it seems that it's possible to intercept the client-server communication and spy in, and
    indeed, this will work with offline mode (warez) servers, however with online mode servers, that's
    where this function comes in!

    Online mode servers rely on an API server from Mojang's (session server), which the client informs
    of the join. The server then queries this server for an acknowledgement of this join, and only if
    this session server confirms that the client did indeed inform it of this join will the server allow
    this client to join.

    The trick is, this request to inform the session server of the join can only be performed by the
    client directly, a proxy can't simulate it, because this request requires a token for the minecraft
    account, which only the launcher has. The client never sends this token to the server, only to the
    Mojang's session server, so a proxy wouldn't have it.

    This join request then contains those 3 variables, one of which being the public key itself, so
    if the proxy sent a different key, the server would no longer arrive at the same server hash, and
    the check would fail, so the server wouldn't allow this client to join.
    """
    public_key_raw = server_public_key.public_bytes(encoding=Encoding.DER, format=PublicFormat.SubjectPublicKeyInfo)

    sha1 = hashlib.sha1()  # noqa: S324 # not used for security
    sha1.update(server_id.encode("utf-8"))
    sha1.update(shared_secret)
    sha1.update(public_key_raw)

    # Minecraft parses the bytes as a signed number, returning it's hex representation as the hexdigest
    base_digest = sha1.digest()
    signed_num = int.from_bytes(base_digest, byteorder="big", signed=True)
    return format(signed_num, "x")


async def join_request(client: httpx.AsyncClient, account: Account, server_hash: str) -> None:
    """Inform the Mojang session server about this new user join.

    This function is called by the client, when joining an online mode (non-warez) server. This is
    required and the server will check that this request was indeed made (:func:`join_check`).

    This request should be performed after receiving the
    :class:`~mcproto.packets.login.login.LoginEncryptionRequest` packet, but before sending the
    :class:`~mcproto.packets.login.login.LoginEncryptionResponse`.

    Performing this request requires an :class:`~mcproto.auth.account.Account` instance, as this request
    is here to ensure that only original Minceraft accounts (officially bought accounts) can join.

    This request uses a ``server_hash`` to identify which server is the client attempting to join. This
    hash is composed of various values, which together serve as a way to prevent any MITMA (man in the
    middle attacks). To obtain this hash, see :func:`compute_server_hash`. This function's docstring
    also includes description for why and how this prevents a MITMA.

    :param client: HTTPX async client to make the HTTP request with.
    :param account: Instance of an account containing the minecraft token necessary for this request.
    :param server_hash: SHA1 hash of the server (see :func:`compute_server_hash`)
    """
    payload = {
        "accessToken": account.access_token,
        "selectedProfile": account.uuid.hex,  # UUID without dashes
        "serverId": server_hash,
    }
    res = await client.post(f"{SESSION_SERVER_URL}/session/minecraft/join", json=payload)

    try:
        res.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise SessionServerError(exc) from exc

    if res.status_code == 204:
        return

    raise ValueError(f"Received unexpected 2XX response: {res.status_code} from sessionserver, but not 204")


async def join_check(
    client: httpx.AsyncClient,
    client_username: str,
    server_hash: str,
    client_ip: str | None = None,
) -> None:
    """Check with the Mojang session server if a join request was made.

    This function is called by the server in online mode (non-warez), to verify that the joining client
    really does have an official minecraft account. The client will first inform the server about this
    join request (:func:`join_request`), server then runs this check confirming the client is who they
    say they are.

    This request should be performed after receiving the after receiving the
    :class:`~mcproto.packets.login.login.LoginEncryptionResponse` packet.

    This request uses a ``server_hash``, this is the value under which the client has submitted their
    join request, and we'll now be checking for that submission with that same value. This is a hash
    composed of various values, which together serve as a way to prevent any MITMA (man in the middle
    attacks). To obtain this hash, see :func:`compute_server_hash`. This function's docstring also
    includes description for why and how this prevents a MITMA.

    :param client: HTTPX async client to make the HTTP request with.
    :param client_username:
        Must match joining the username of the joining client (case sensitive).

        Note: This is the in-game nickname of the selected profile, not Mojang account name
        (which is never sent to the server). Servers should use the name in "name" field which was
        received in the :class:`~mcproto.packets.login.login.LoginStart` packet.
    :param server_hash: SHA1 hash of the server (see :func:`compute_server_hash`)
    :param client_ip:
        IP address of the connecting player (optional)

        Servers only include this when 'prevent-proxy-connections' is set to true in server.properties
    """
    res = await client.post(
        f"{SESSION_SERVER_URL}/session/minecraft/hasJoined",
        params={"username": client_username, "serverId": server_hash, "ip": client_ip},
    )
    res.raise_for_status()
    data: JoinAcknowledgeData = res.json()

    McUUID(data["id"])
    data["name"]
