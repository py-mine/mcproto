from __future__ import annotations

from enum import StrEnum
from typing import NamedTuple

import httpx
from typing_extensions import Self

__all__ = [
    "XSTSErrorType",
    "XSTSRequestError",
    "xbox_auth",
]

XBOX_LIVE_AUTH_URL = "https://user.auth.xboxlive.com/user/authenticate"
XBOX_SECURE_TOKEN_SERVER_AUTH_URL = "https://xsts.auth.xboxlive.com/xsts/authorize"  # noqa: S105


class XSTSErrorType(StrEnum):
    NO_XBOX_ACCOUNT = (
        "The account doesn't have an Xbox account. Once they sign up for one (or login through minecraft.net to create"
        " one) then they can proceed with the login. This shouldn't happen with accounts that have purchased Minecraft"
        " with a Microsoft account, as they would've already gone through that Xbox signup process."
    )
    XBOX_LIVE_NOT_IN_COUNTRY = "The account is from a country where Xbox Live is not available/banned"
    ADULT_VERIFICATION_NEEDED = "The account needs adult verification on Xbox page. (South Korea)"
    UNDERAGE_ACCOUNT = (
        "The account is a child (under 18) and cannot proceed unless the account is added to a Family by an adult."
        " This only seems to occur when using a custom Microsoft Azure application. When using the Minecraft launchers"
        " client id, this doesn't trigger."
    )
    UNKNOWN = "This is an unknown error."

    @classmethod
    def from_status_error(cls, xerr_no: int) -> Self:
        if xerr_no == 2148916233:
            return cls.NO_XBOX_ACCOUNT
        if xerr_no == 2148916235:
            return cls.XBOX_LIVE_NOT_IN_COUNTRY
        if xerr_no == 2148916236 or xerr_no == 2148916237:
            return cls.ADULT_VERIFICATION_NEEDED
        if xerr_no == 2148916238:
            return cls.UNDERAGE_ACCOUNT

        return cls.UNKNOWN


class XSTSRequestError(Exception):
    def __init__(self, exc: httpx.HTTPStatusError):
        self.status_error = exc

        data = exc.response.json()
        self.identity: str = data["Identity"]
        self.xerr: int = data["XErr"]
        self.message: str = data["Message"]
        self.redirect_url: str = data["Redirect"]
        self.err_type = XSTSErrorType.from_status_error(self.xerr)

        return super().__init__(self.msg)

    @property
    def msg(self) -> str:
        msg_parts = []
        if self.err_type is not XSTSErrorType.UNKNOWN:
            msg_parts.append(f"{self.err_type.name}: {self.err_type.value!r}")
        else:
            msg_parts.append(f"identity={self.identity!r}")
            msg_parts.append(f"xerr-{self.xerr}")
            msg_parts.append(f"message={self.message!r}")
            msg_parts.append(f"redirect_url={self.redirect_url!r}")

        return " ".join(msg_parts)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.msg})"


class XboxData(NamedTuple):
    user_hash: str
    xsts_token: str


async def xbox_auth(client: httpx.AsyncClient, microsoft_access_token: str, bedrock: bool = False) -> XboxData:
    """Authenticate into Xbox Live account and obtain user hash and XSTS token."""
    # Obtain XBL token
    payload = {
        "Properties": {
            "AuthMethod": "RPS",
            "SiteName": "user.auth.xboxlive.com",
            "RpsTicket": f"d={microsoft_access_token}",
        },
        "RelyingParty": "http://auth.xboxlive.com",
        "TokenType": "JWT",
    }
    res = await client.post(XBOX_LIVE_AUTH_URL, json=payload)
    res.raise_for_status()
    data = res.json()

    xbl_token = data["Token"]
    user_hash = data["DisplayClaims"]["xui"][0]["uhs"]

    # Obtain XSTS token
    payload = {
        "Properties": {
            "SandboxId": "RETAIL",
            "UserTokens": [xbl_token],
        },
        "RelyingParty": "https://pocket.realms.minecraft.net" if bedrock else "rp://api.minecraftservices.com/",
        "TokenType": "JWT",
    }
    res = await client.post(XBOX_SECURE_TOKEN_SERVER_AUTH_URL, json=payload)

    try:
        res.raise_for_status()
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 401:
            raise XSTSRequestError(exc) from exc
        raise
    data = res.json()

    xsts_token = data["Token"]

    return XboxData(user_hash=user_hash, xsts_token=xsts_token)
