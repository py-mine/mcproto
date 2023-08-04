from __future__ import annotations

from enum import Enum

import httpx
from typing_extensions import Self

from mcproto.auth.account import Account
from mcproto.types.uuid import UUID as McUUID  # noqa: N811

__all__ = [
    "ServicesAPIError",
    "ServicesAPIErrorType",
    "MSAAccount",
]

MC_SERVICES_API_URL = "https://api.minecraftservices.com"


class ServicesAPIErrorType(str, Enum):
    INVALID_REGISTRATION = "Invalid app registration, see https://aka.ms/AppRegInfo for more information"
    UNKNOWN = "This is an unknown error."

    @classmethod
    def from_status_error(cls, code: int, err_msg: str | None) -> Self:
        if code == 401 and err_msg == "Invalid app registration, see https://aka.ms/AppRegInfo for more information":
            return cls.INVALID_REGISTRATION
        return cls.UNKNOWN


class ServicesAPIError(Exception):
    def __init__(self, exc: httpx.HTTPStatusError):
        self.status_error = exc
        self.code = exc.response.status_code
        self.url = exc.request.url

        data = exc.response.json()
        self.err_msg: str | None = data.get("errorMessage")
        self.err_type = ServicesAPIErrorType.from_status_error(self.code, self.err_msg)

        super().__init__(self.msg)

    @property
    def msg(self) -> str:
        msg_parts = []
        msg_parts.append(f"HTTP {self.code} from {self.url}:")
        msg_parts.append(f"type={self.err_type.name!r}")

        if self.err_type is not ServicesAPIErrorType.UNKNOWN:
            msg_parts.append(f"details={self.err_type.value!r}")
        elif self.err_msg is not None:
            msg_parts.append(f"msg={self.err_msg!r}")

        return " ".join(msg_parts)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.msg})"


class MSAAccount(Account):
    __slots__ = ()

    @staticmethod
    async def _get_access_token_from_xbox(client: httpx.AsyncClient, user_hash: str, xsts_token: str) -> str:
        """Obtain access token from an XSTS token from Xbox Live auth (for Microsoft accounts)."""
        payload = {"identityToken": f"XBL3.0 x={user_hash};{xsts_token}"}
        res = await client.post(f"{MC_SERVICES_API_URL}/authentication/login_with_xbox", json=payload)

        try:
            res.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise ServicesAPIError(exc) from exc

        data = res.json()
        return data["access_token"]

    @classmethod
    async def from_xbox_access_token(cls, client: httpx.AsyncClient, access_token: str) -> Self:
        """Construct the account from the xbox access token, using it to get the rest of the profile information."""
        res = await client.get(
            f"{MC_SERVICES_API_URL}/minecraft/profile", headers={"Authorization": f"Bearer {access_token}"}
        )
        res.raise_for_status()
        data = res.json()

        return cls(data["name"], McUUID(data["id"]), access_token)

    @classmethod
    async def xbox_auth(cls, client: httpx.AsyncClient, user_hash: str, xsts_token: str) -> Self:
        """Authenticate using an XSTS token from Xbox Live auth (for Microsoft accounts)."""
        access_token = await cls._get_access_token_from_xbox(client, user_hash, xsts_token)
        return await cls.from_xbox_access_token(client, access_token)
