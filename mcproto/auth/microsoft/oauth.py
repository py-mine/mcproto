from __future__ import annotations

import asyncio
from enum import Enum
from typing import TypedDict

import httpx
from typing_extensions import Self

__all__ = [
    "MicrosoftOauthResponseErrorType",
    "MicrosoftOauthResponseError",
    "MicrosoftOauthRequestData",
    "MicrosoftOauthResponseData",
    "microsoft_oauth_request",
    "microsoft_oauth_authenticate",
    "full_microsoft_oauth",
]

MICROSOFT_OAUTH_URL = "https://login.microsoftonline.com/consumers/oauth2/v2.0"


class MicrosoftOauthResponseErrorType(str, Enum):
    """Enum for various different kinds of exceptions that the Microsoft OAuth2 API can report."""

    AUTHORIZATION_PENDING = "The user hasn't finished authenticating, but hasn't canceled the flow."
    AUTHORIZATION_DECLINED = "The end user denied the authorization request."
    BAD_VERIFICATION_CODE = "The device_code sent to the /token endpoint wasn't recognized."
    EXPIRED_TOKEN = (
        "Value of expires_in has been exceeded and authentication is no longer possible"  # noqa: S105
        " with device_code."
    )
    INVALID_GRANT = "The provided value for the input parameter 'device_code' is not valid."
    UNKNOWN = "This is an unknown error"

    @classmethod
    def from_status_error(cls, error: str) -> Self:
        """Determine the error kind based on the error data."""
        if error == "expired_token":
            return cls.EXPIRED_TOKEN
        if error == "authorization_pending":
            return cls.AUTHORIZATION_PENDING
        if error == "authorization_declined":
            return cls.AUTHORIZATION_DECLINED
        if error == "bad_verification_code":
            return cls.BAD_VERIFICATION_CODE
        if error == "invald_grant":
            return cls.INVALID_GRANT
        return cls.UNKNOWN


class MicrosoftOauthResponseError(Exception):
    """Exception raised on a failure from the Microsoft OAuth2 API."""

    def __init__(self, exc: httpx.HTTPStatusError):
        self.status_error = exc

        data = exc.response.json()
        self.error = data["error"]
        self.err_type = MicrosoftOauthResponseErrorType.from_status_error(self.error)

        super().__init__(self.err_type.value)

    def __repr__(self) -> str:
        if self.err_type is MicrosoftOauthResponseErrorType.UNKNOWN:
            msg = f"Unknown error: {self.error!r}"
        else:
            msg = f"Error {self.err_type.name}: {self.err_type.value!r}"

        return f"{self.__class__.__name__}({msg})"


class MicrosoftOauthRequestData(TypedDict):
    """Data obtained from Microsoft OAuth2 API after making a new authentication request.

    This data specifies where (URL) we can check with the Microsoft OAuth2 servers for a client
    confirmation of this authentication request, how often we should check with this server, and
    when this request expires.
    """

    user_code: str
    device_code: str
    verification_url: str
    expires_in: int
    interval: int
    message: str


class MicrosoftOauthResponseData(TypedDict):
    """Data obtained from Microsoft OAuth2 API after a successful authentication.

    This data contains the access and refresh tokens, giving us the requested account access
    and the expiry information.
    """

    token_type: str
    scope: str
    expires_in: int
    access_token: str
    refresh_token: str
    id_token: str


async def microsoft_oauth_request(client: httpx.AsyncClient, client_id: str) -> MicrosoftOauthRequestData:
    """Initiate Microsoft Oauth2 flow.

    This requires a ``client_id``, which can be obtained by creating an application on
    `Microsoft Azure <https://learn.microsoft.com/en-us/azure/active-directory/develop/quickstart-register-app>`_,
    with 'Allow public client flows' set to 'Yes' (can be set from the 'Authentication' tab).

    This will create a device id, used to identify our request and a user code, which the user can manually enter to
    https://www.microsoft.com/link and confirm, after that, :func:`microsoft_oauth_authenticate` should be called,
    with the returend device id as an argument.
    """
    data = {"client_id": client_id, "scope": "XboxLive.signin offline_access"}
    res = await client.post(f"{MICROSOFT_OAUTH_URL}/devicecode", data=data)
    res.raise_for_status()

    return res.json()


async def microsoft_oauth_authenticate(
    client: httpx.AsyncClient,
    client_id: str,
    device_code: str,
) -> MicrosoftOauthResponseData:
    """Complete Microsoft Oauth2 flow and authenticate.

    This functon should be called after :func:`microsoft_oauth_request`. If the user has authorized the request,
    we will get an access token back, allowing us to perform certain actions on behaf of the microsoft user that
    has authorized this request. Alternatively, this function will fal with :exc:`MicrosoftOauthResponseError`.
    """
    data = {
        "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
        "client_id": client_id,
        "device_code": device_code,
    }
    res = await client.post(f"{MICROSOFT_OAUTH_URL}/token", data=data)

    try:
        res.raise_for_status()
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 400:
            raise MicrosoftOauthResponseError(exc) from exc
        raise

    return res.json()


async def full_microsoft_oauth(client: httpx.AsyncClient, client_id: str) -> MicrosoftOauthResponseData:
    """Perform full Microsoft Oauth2 sequence, waiting for user to authenticated (from the browser).

    See :func:`microsoft_oauth_request` (OAuth2 start) and :func:`microsoft_oauth_authenticate` (OAuth2 end).
    """
    request_data = await microsoft_oauth_request(client, client_id)

    # Contains instructions for the user (user code and verification url)
    print(request_data["message"])  # noqa: T201

    while True:
        await asyncio.sleep(request_data["interval"])
        try:
            return await microsoft_oauth_authenticate(client, client_id, request_data["device_code"])
        except MicrosoftOauthResponseError as exc:
            if exc.err_type is MicrosoftOauthResponseErrorType.AUTHORIZATION_PENDING:
                continue
            raise
