from __future__ import annotations

import httpx
from typing_extensions import override

from mcproto.types.uuid import UUID as McUUID  # noqa: N811

MINECRAFT_API_URL = "https://api.minecraftservices.com"

__all__ = [
    "Account",
    "InvalidAccountAccessTokenError",
    "MismatchedAccountInfoError",
]


class MismatchedAccountInfoError(Exception):
    """Exception raised when info stored in the account instance doesn't match one from API."""

    def __init__(self, mismatched_variable: str, current: object, expected: object) -> None:
        self.missmatched_variable = mismatched_variable
        self.current = current
        self.expected = expected
        super().__init__(repr(self))

    @override
    def __repr__(self) -> str:
        msg = f"Account has mismatched {self.missmatched_variable}: "
        msg += f"current={self.current!r}, expected={self.expected!r}."

        return f"{self.__class__.__name__}({msg!r})"


class InvalidAccountAccessTokenError(Exception):
    """Exception raised when the access token of the account was reported as invalid."""

    def __init__(self, access_token: str, status_error: httpx.HTTPStatusError) -> None:
        self.access_token = access_token
        self.status_error = status_error
        super().__init__("The account access token used is not valid (key expired?)")


class Account:
    """Base class for an authenticated Minecraft account."""

    __slots__ = ("access_token", "username", "uuid")

    username: str
    uuid: McUUID
    access_token: str

    def __init__(self, username: str, uuid: McUUID, access_token: str) -> None:
        self.username = username
        self.uuid = uuid
        self.access_token = access_token

    async def check(self, client: httpx.AsyncClient) -> None:
        """Check with minecraft API whether the account information stored is valid.

        Raises:
            MismatchedAccountInfoError:
                If the information received from the minecraft API didn't match the information currently
                stored in the account instance.
            InvalidAccountAccessTokenError: If the access token is not valid.
        """
        res = await client.get(
            f"{MINECRAFT_API_URL}/minecraft/profile",
            headers={"Authorization": f"Bearer {self.access_token}"},
        )

        try:
            _ = res.raise_for_status()
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 401:
                raise InvalidAccountAccessTokenError(self.access_token, exc) from exc
            raise
        data = res.json()

        if self.uuid != McUUID(data["id"]):
            raise MismatchedAccountInfoError("uuid", self.uuid, data["id"])
        if self.username != data["name"]:
            raise MismatchedAccountInfoError("username", self.username, data["name"])
