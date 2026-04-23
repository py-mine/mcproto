from __future__ import annotations

import warnings
from enum import Enum
from uuid import uuid4

import httpx
from typing_extensions import Any, Self, override

from mcproto.auth.account import Account
from mcproto.types.uuid import UUID as McUUID  # noqa: N811

__all__ = [
    "AuthServerApiError",
    "AuthServerApiErrorType",
    "YggdrasilAccount",
]

AUTHSERVER_API_URL = "https://authserver.mojang.com"


class AuthServerApiErrorType(str, Enum):
    """Enum for various different kinds of exceptions that the authserver API can report."""

    MICROSOFT_MIGRATED = "This Minecraft account was migrated, use Microsoft OAuth2 login instaed."
    FORBIDDEN = "An attempt to sign in using empty or insufficiently short credentials."
    INVALID_CREDENTIALS = (
        "Either a successful attempt to sign in using an account with excessive login attempts"
        " or an unsuccessful attempt to sign in using a non-existent account."
    )
    MOJANG_MIGRATED = (
        "Attempted to login with username (Mojang accounts only), howver this account was"
        " already migrated into a Minecraft account. Use E-Mail to login instead of username."
    )
    INVALID_TOKEN_REFRESH = (
        "An attempt to refresh an access token that has been invalidated, "  # noqa: S105
        "no longer exists or has been ereased."
    )
    INVALID_TOKEN_VALIDATE = (
        "An attempt to validate an access token obtained from /authenticate endpoint that has"  # noqa: S105
        " expired or become invalid while under rate-limiting conditions."
    )
    UNKNOWN = "This is an unknown error."

    @classmethod
    def from_status_error(
        cls,
        code: int,
        short_msg: str,
        full_msg: str,
        cause_msg: str | None,
    ) -> AuthServerApiErrorType:
        """Determine the error kind based on the error data."""
        if code == 410:
            return cls.MICROSOFT_MIGRATED
        if code == 403:
            if full_msg == "Forbidden":
                return cls.FORBIDDEN
            if full_msg == "Invalid credentials. Invalid username or password.":
                return cls.INVALID_CREDENTIALS
            if full_msg == "Invalid credentials. Account migrated, use email as username.":
                return cls.MOJANG_MIGRATED
            if full_msg == "Token does not exist":
                return cls.INVALID_TOKEN_REFRESH
        if code == 429 and full_msg == "Invalid token.":
            return cls.INVALID_TOKEN_VALIDATE

        return cls.UNKNOWN


class AuthServerApiError(Exception):
    """Exception raised on a failure from the authserver API."""

    def __init__(self, exc: httpx.HTTPStatusError):
        self.status_error = exc
        self.code = exc.response.status_code
        self.url = exc.request.url

        data = exc.response.json()
        self.short_msg: str = data["error"]
        self.full_msg: str = data["errorMessage"]
        self.cause_msg: str = data.get("cause")
        self.err_type = AuthServerApiErrorType.from_status_error(
            self.code, self.short_msg, self.cause_msg, self.full_msg
        )

        super().__init__(self.msg)

    @property
    def msg(self) -> str:
        """Produce a message for this error."""
        msg_parts: list[str] = []
        msg_parts.append(f"HTTP {self.code} from {self.url}:")
        msg_parts.append(f"type={self.err_type.name!r}")

        if self.err_type is not AuthServerApiErrorType.UNKNOWN:
            msg_parts.append(f"msg={self.err_type.value!r}")
        else:
            msg_parts.append(f"short_msg={self.short_msg!r}")
            msg_parts.append(f"full_msg={self.full_msg!r}")
            msg_parts.append(f"cause_msg={self.cause_msg!r}")

        return " ".join(msg_parts)

    @override
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.msg})"


class YggdrasilAccount(Account):
    """Minecraft account logged into using Yggdrasil (legacy/unmigrated) auth system."""

    __slots__ = ("client_token",)

    def __init__(self, username: str, uuid: McUUID, access_token: str, client_token: str | None) -> None:
        super().__init__(username, uuid, access_token)

        if client_token is None:
            client_token = str(uuid4())
        self.client_token = client_token

    async def refresh(self, client: httpx.AsyncClient) -> None:
        """Refresh the Yggdrasil access token.

        This method can be called when the access token expires, to obtain a new one without
        having to go through a complete re-login. This can happen after some time period, or
        for example when someone else logs in to this minecraft account elsewhere.
        """
        payload: dict[str, Any] = {
            "accessToken": self.access_token,
            "clientToken": self.client_token,
            "selectedProfile": {"id": str(self.uuid), "name": self.username},
        }
        res = await client.post(
            f"{AUTHSERVER_API_URL}/refresh",
            headers={"content-type": "application/json"},
            json=payload,
        )

        try:
            _ = res.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise AuthServerApiError(exc) from exc

        data = res.json()

        if (recv_client_token := data["clientToken"]) != self.client_token:
            raise ValueError(f"Missmatched client tokens! {recv_client_token!r} != {self.client_token!r}")

        if (recv_uuid := McUUID(data["selectedProfile"]["uuid"])) != self.uuid:
            # The UUID really shouldn't be different here, but if it is, update it, as it's more recent.
            # However it's incredibly weird if this really would happen, so a warning is emitted.
            warnings.warn(
                f"Player UUID changed after refresh ({self.uuid!r} -> {recv_uuid!r})",
                UserWarning,
                stacklevel=2,
            )
            self.uuid = recv_uuid

        # in case username changed
        self.username = data["selectedProfile"]["name"]

        # new (refreshed) access token
        self.access_token = data["accessToken"]

    async def validate(self, client: httpx.AsyncClient) -> bool:
        """Check if the access token is (still) usable for authentication with a Minecraft server.

        If this method fails, the stored access token is no longer usable for for authentcation
        with a Minecraft server, but should still be good enough for [`refresh`][..].

        This mainly happens when one has used another client (e.g. another launcher).
        """
        # The payload can also include a client token (same as the one used in auth), but it's
        # not necessary, and the official launcher doesn't send it, so we won't either
        payload = {"accessToken": self.access_token}
        res = await client.post(f"{AUTHSERVER_API_URL}/validate", json=payload)

        if res.status_code == 204:
            return True

        try:
            _ = res.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise AuthServerApiError(exc) from exc

        raise ValueError(f"Received unexpected 2XX response: {res.status_code} from /validate, but not 204")

    @classmethod
    async def authenticate(cls, client: httpx.AsyncClient, login: str, password: str) -> Self:
        """Authenticate using the Yggdrasil system (for non-Microsoft accounts).

        Args:
            login: E-Mail of your Minecraft account, or username for (really old) Mojang accounts.
            password: Plaintext account password.
        """
        # Any random string, we use a random v4 uuid, needs to remain same in further communications
        client_token = str(uuid4())

        payload: dict[str, Any] = {
            "agent": {
                "name": "Minecraft",
                "version": 1,
            },
            "username": login,
            "password": password,
            "clientToken": client_token,
            "requestUser": False,
        }
        res = await client.post(f"{AUTHSERVER_API_URL}/authenticate", json=payload)

        try:
            _ = res.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise AuthServerApiError(exc) from exc

        data = res.json()

        if (recv_client_token := data["clientToken"]) != client_token:
            raise ValueError(f"Missmatched client tokens! {recv_client_token!r} != {client_token!r}")

        username = data["selectedProfile"]["name"]
        uuid = McUUID(data["selectedProfile"]["uuid"])
        access_token = data["accessToken"]

        return cls(username, uuid, access_token, client_token)

    async def signout(self, client: httpx.AsyncClient, username: str, password: str) -> None:
        """Sign out using the Yggdrasil system (for non-Microsoft accounts).

        Args:
            login: E-Mail of your Minecraft account, or username for (really old) Mojang accounts.
            password: Plaintext account password.
        """
        payload = {
            "username": username,
            "password": password,
        }
        res = await client.post(f"{AUTHSERVER_API_URL}/signout", json=payload)

        try:
            _ = res.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise AuthServerApiError(exc) from exc

        # Status code is 2XX, meaning we succeeded (response doesn't contain any payload)
