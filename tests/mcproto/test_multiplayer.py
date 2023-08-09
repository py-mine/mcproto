import sys
from unittest.mock import Mock

import httpx
import pytest
from pytest_httpx import HTTPXMock

from mcproto.multiplayer import (
    JoinAcknowledgeData,
    JoinAcknowledgeProperty,
    SESSION_SERVER_URL,
    SessionServerError,
    SessionServerErrorType,
    UserJoinCheckFailedError,
    compute_server_hash,
    join_check,
    join_request,
)
from tests.mcproto.test_encryption import RSA_PUBLIC_KEY


@pytest.mark.skipif(sys.version_info < (3, 9), reason="requires 3.9+ for pytest-httpx dependency")
async def test_join_request_valid(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url=f"{SESSION_SERVER_URL}/session/minecraft/join",
        method="POST",
        status_code=204,
    )

    account = Mock()
    account.access_token = "foobar"  # noqa: S105 # hard-coded password
    account.uuid.hex = "97e071429b5e49b19c15d16232a93746"
    server_hash = "-745fc7fdb2d6ae7c4b20e2987770def8f3dd1105"

    async with httpx.AsyncClient() as client:
        await join_request(client, account, server_hash)


@pytest.mark.skipif(sys.version_info < (3, 9), reason="requires 3.9+ for pytest-httpx dependency")
@pytest.mark.parametrize(
    ("status_code", "err_msg", "err_type"),
    [
        (403, "InsufficientPrivilegesException", SessionServerErrorType.XBOX_MULTIPLAYER_DISABLED),
        (403, "UserBannedException", SessionServerErrorType.BANNED_FROM_MULTIPLAYER),
        (403, "ForbiddenOperationException", SessionServerErrorType.UNKNOWN),
    ],
)
async def test_join_request_invalid(
    status_code: int,
    err_msg: str,
    err_type: SessionServerErrorType,
    httpx_mock: HTTPXMock,
) -> None:
    httpx_mock.add_response(
        url=f"{SESSION_SERVER_URL}/session/minecraft/join",
        method="POST",
        status_code=status_code,
        json={"error": err_msg, "path": "/session/minecraft/join"},
    )

    account = Mock()
    account.access_token = "foobar"  # noqa: S105 # hard-coded password
    account.uuid.hex = "97e071429b5e49b19c15d16232a93746"
    server_hash = "-745fc7fdb2d6ae7c4b20e2987770def8f3dd1105"

    async with httpx.AsyncClient() as client:
        with pytest.raises(SessionServerError) as exc_info:
            await join_request(client, account, server_hash)

        exc = exc_info.value
        assert exc.code == status_code
        assert exc.url == f"{SESSION_SERVER_URL}/session/minecraft/join"
        assert exc.err_msg == err_msg
        assert exc.err_type is err_type


@pytest.mark.skipif(sys.version_info < (3, 9), reason="requires 3.9+ for pytest-httpx dependency")
@pytest.mark.parametrize(
    ("client_ip"),
    [
        (None),
        ("172.17.0.1"),
    ],
)
async def test_join_check_valid(client_ip, httpx_mock: HTTPXMock):
    client_username = "ItsDrike"
    server_hash = "-745fc7fdb2d6ae7c4b20e2987770def8f3dd1105"
    ack_data = JoinAcknowledgeData(
        {
            "id": "1759517ef05a4bcd8c8b116fa31c1bbd",
            "name": "ItsDrike",
            "properties": [
                JoinAcknowledgeProperty(
                    {
                        "name": "textures",
                        "value": "",
                        "signature": "",
                    }
                )
            ],
        }
    )

    params = {"username": client_username, "serverId": server_hash}
    if client_ip is not None:
        params["ip"] = client_ip
    url = httpx.URL(f"{SESSION_SERVER_URL}/session/minecraft/hasJoined", params=params)

    httpx_mock.add_response(
        url=str(url),
        method="GET",
        status_code=200,
        json=ack_data,
    )

    async with httpx.AsyncClient() as client:
        ret_data = await join_check(client, client_username, server_hash, client_ip)

    assert ret_data == ack_data


@pytest.mark.skipif(sys.version_info < (3, 9), reason="requires 3.9+ for pytest-httpx dependency")
async def test_join_check_invalid(httpx_mock: HTTPXMock):
    client_username = "ItsDrike"
    server_hash = "-745fc7fdb2d6ae7c4b20e2987770def8f3dd1105"
    client_ip = None

    params = {"username": client_username, "serverId": server_hash}
    if client_ip is not None:
        params["ip"] = client_ip
    url = httpx.URL(f"{SESSION_SERVER_URL}/session/minecraft/hasJoined", params=params)

    httpx_mock.add_response(
        url=str(url),
        method="GET",
        status_code=204,
    )

    async with httpx.AsyncClient() as client:
        with pytest.raises(UserJoinCheckFailedError) as exc_info:
            await join_check(client, client_username, server_hash, client_ip)

        exc = exc_info.value
        assert exc.client_username == client_username
        assert exc.server_hash == server_hash
        assert exc.client_ip == client_ip


def test_compute_server_hash():
    server_id = ""
    shared_secret = bytes.fromhex("f71e3033d4c0fc6aadee4417831b5c3e")
    server_public_key = RSA_PUBLIC_KEY
    expected_server_hash = "-745fc7fdb2d6ae7c4b20e2987770def8f3dd1105"

    assert compute_server_hash(server_id, shared_secret, server_public_key) == expected_server_hash
