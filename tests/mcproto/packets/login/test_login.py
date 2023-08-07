from __future__ import annotations

from typing import Any

import pytest

from mcproto.buffer import Buffer
from mcproto.packets.login.login import (
    LoginDisconnect,
    LoginEncryptionRequest,
    LoginEncryptionResponse,
    LoginPluginRequest,
    LoginPluginResponse,
    LoginSetCompression,
    LoginStart,
    LoginSuccess,
)
from mcproto.types.chat import ChatMessage
from mcproto.types.uuid import UUID
from tests.mcproto.test_encryption import RSA_PUBLIC_KEY


class TestLoginStart:
    @pytest.mark.parametrize(
        ("kwargs", "expected_bytes"),
        [
            (
                {"username": "ItsDrike", "uuid": UUID("f70b4a42c9a04ffb92a31390c128a1b2")},
                bytes.fromhex("084974734472696b6501f70b4a42c9a04ffb92a31390c128a1b2"),
            ),
            (
                {"username": "foobar1", "uuid": UUID("7a82476416fc4e8b8686a99c775db7d3")},
                bytes.fromhex("07666f6f62617231017a82476416fc4e8b8686a99c775db7d3"),
            ),
        ],
    )
    def test_serialize(self, kwargs: dict[str, Any], expected_bytes: bytes):
        packet = LoginStart(**kwargs)
        assert packet.serialize().flush() == bytearray(expected_bytes)

    @pytest.mark.parametrize(
        ("input_bytes", "expected_args"),
        [
            (
                bytes.fromhex("084974734472696b6501f70b4a42c9a04ffb92a31390c128a1b2"),
                {"username": "ItsDrike", "uuid": UUID("f70b4a42c9a04ffb92a31390c128a1b2")},
            ),
            (
                bytes.fromhex("07666f6f62617231017a82476416fc4e8b8686a99c775db7d3"),
                {"username": "foobar1", "uuid": UUID("7a82476416fc4e8b8686a99c775db7d3")},
            ),
        ],
    )
    def test_deserialize(self, input_bytes: bytes, expected_args: dict[str, Any]):
        packet = LoginStart.deserialize(Buffer(input_bytes))
        for arg_name, val in expected_args.items():
            assert getattr(packet, arg_name) == val


class TestLoginEncryptionRequest:
    @pytest.mark.parametrize(
        ("kwargs", "expected_bytes"),
        [
            (
                {"public_key": RSA_PUBLIC_KEY, "verify_token": bytes.fromhex("9bd416ef"), "server_id": "a" * 20},
                bytes.fromhex(
                    "146161616161616161616161616161616161616161a20130819f300d06092a864886f70d010101050003818d003081890"
                    "2818100cb515109911ea3e4740d8a17a7ccd9cf226c83c7615e4a5505cd124571ee210a4ba26c7c42e15f51fcb7fa90dc"
                    "e6f83ebe0e163817c7d9fb1af7d981e90da2cc06ea59d01ff9fbb76b1803a0fe5af4a2c75145d89eb03e6a4aae21d2e7d"
                    "4c3938a298da575e12e0ae178d61a69bc0ea0b381790f182d9dba715bfb503c99d92b0203010001049bd416ef"
                ),
            ),
        ],
    )
    def test_serialize(self, kwargs: dict[str, Any], expected_bytes: bytes):
        packet = LoginEncryptionRequest(**kwargs)
        assert packet.serialize().flush() == bytearray(expected_bytes)

    @pytest.mark.parametrize(
        ("input_bytes", "expected_args"),
        [
            (
                bytes.fromhex(
                    "146161616161616161616161616161616161616161a20130819f300d06092a864886f70d010101050003818d003081890"
                    "2818100cb515109911ea3e4740d8a17a7ccd9cf226c83c7615e4a5505cd124571ee210a4ba26c7c42e15f51fcb7fa90dc"
                    "e6f83ebe0e163817c7d9fb1af7d981e90da2cc06ea59d01ff9fbb76b1803a0fe5af4a2c75145d89eb03e6a4aae21d2e7d"
                    "4c3938a298da575e12e0ae178d61a69bc0ea0b381790f182d9dba715bfb503c99d92b0203010001049bd416ef"
                ),
                {"public_key": RSA_PUBLIC_KEY, "verify_token": bytes.fromhex("9bd416ef"), "server_id": "a" * 20},
            ),
        ],
    )
    def test_deserialize(self, input_bytes: bytes, expected_args: dict[str, Any]):
        packet = LoginEncryptionRequest.deserialize(Buffer(input_bytes))
        for arg_name, val in expected_args.items():
            assert getattr(packet, arg_name) == val


class TestLoginEncryptionResponse:
    @pytest.mark.parametrize(
        ("kwargs", "expected_bytes"),
        [
            (
                {"shared_secret": b"I'm shared", "verify_token": b"Token"},
                bytes.fromhex("0a49276d2073686172656405546f6b656e"),
            )
        ],
    )
    def test_serialize(self, kwargs: dict[str, Any], expected_bytes: bytes):
        packet = LoginEncryptionResponse(**kwargs)
        assert packet.serialize().flush() == bytearray(expected_bytes)

    @pytest.mark.parametrize(
        ("input_bytes", "expected_args"),
        [
            (
                bytes.fromhex("0a49276d2073686172656405546f6b656e"),
                {"shared_secret": b"I'm shared", "verify_token": b"Token"},
            )
        ],
    )
    def test_deserialize(self, input_bytes: bytes, expected_args: dict[str, Any]):
        packet = LoginEncryptionResponse.deserialize(Buffer(input_bytes))
        for arg_name, val in expected_args.items():
            assert getattr(packet, arg_name) == val


class TestLoginSuccess:
    @pytest.mark.parametrize(
        ("kwargs", "expected_bytes"),
        [
            (
                {"uuid": UUID("f70b4a42c9a04ffb92a31390c128a1b2"), "username": "Mario"},
                bytes.fromhex("f70b4a42c9a04ffb92a31390c128a1b2054d6172696f"),
            )
        ],
    )
    def test_serialize(self, kwargs: dict[str, Any], expected_bytes: bytes):
        packet = LoginSuccess(**kwargs)
        assert packet.serialize().flush() == bytearray(expected_bytes)

    @pytest.mark.parametrize(
        ("input_bytes", "expected_args"),
        [
            (
                bytes.fromhex("f70b4a42c9a04ffb92a31390c128a1b2054d6172696f"),
                {"uuid": UUID("f70b4a42c9a04ffb92a31390c128a1b2"), "username": "Mario"},
            )
        ],
    )
    def test_deserialize(self, input_bytes: bytes, expected_args: dict[str, Any]):
        packet = LoginSuccess.deserialize(Buffer(input_bytes))
        for arg_name, val in expected_args.items():
            assert getattr(packet, arg_name) == val


class TestLoginDisconnect:
    @pytest.mark.parametrize(
        ("kwargs", "expected_bytes"),
        [
            (
                {"reason": ChatMessage("You are banned.")},
                bytes.fromhex("1122596f75206172652062616e6e65642e22"),
            )
        ],
    )
    def test_serialize(self, kwargs: dict[str, Any], expected_bytes: bytes):
        packet = LoginDisconnect(**kwargs)
        assert packet.serialize().flush() == bytearray(expected_bytes)

    @pytest.mark.parametrize(
        ("input_bytes", "expected_args"),
        [
            (
                bytes.fromhex("1122596f75206172652062616e6e65642e22"),
                {"reason": ChatMessage("You are banned.")},
            )
        ],
    )
    def test_deserialize(self, input_bytes: bytes, expected_args: dict[str, Any]):
        packet = LoginDisconnect.deserialize(Buffer(input_bytes))
        for arg_name, val in expected_args.items():
            assert getattr(packet, arg_name) == val


class TestLoginPluginRequest:
    @pytest.mark.parametrize(
        ("kwargs", "expected_bytes"),
        [
            (
                {"message_id": 0, "channel": "xyz", "data": b"Hello"},
                bytes.fromhex("000378797a48656c6c6f"),
            )
        ],
    )
    def test_serialize(self, kwargs: dict[str, Any], expected_bytes: bytes):
        packet = LoginPluginRequest(**kwargs)
        assert packet.serialize().flush() == bytearray(expected_bytes)

    @pytest.mark.parametrize(
        ("input_bytes", "expected_args"),
        [
            (
                bytes.fromhex("000378797a48656c6c6f"),
                {"message_id": 0, "channel": "xyz", "data": b"Hello"},
            )
        ],
    )
    def test_deserialize(self, input_bytes: bytes, expected_args: dict[str, Any]):
        packet = LoginPluginRequest.deserialize(Buffer(input_bytes))
        for arg_name, val in expected_args.items():
            assert getattr(packet, arg_name) == val


class TestLoginPluginResponse:
    @pytest.mark.parametrize(
        ("kwargs", "expected_bytes"),
        [
            (
                {"message_id": 0, "data": b"Hello"},
                bytes.fromhex("000148656c6c6f"),
            )
        ],
    )
    def test_serialize(self, kwargs: dict[str, Any], expected_bytes: bytes):
        packet = LoginPluginResponse(**kwargs)
        assert packet.serialize().flush() == bytearray(expected_bytes)

    @pytest.mark.parametrize(
        ("input_bytes", "expected_args"),
        [
            (
                bytes.fromhex("000148656c6c6f"),
                {"message_id": 0, "data": b"Hello"},
            )
        ],
    )
    def test_deserialize(self, input_bytes: bytes, expected_args: dict[str, Any]):
        packet = LoginPluginResponse.deserialize(Buffer(input_bytes))
        for arg_name, val in expected_args.items():
            assert getattr(packet, arg_name) == val


class TestLoginSetCompression:
    @pytest.mark.parametrize(
        ("kwargs", "expected_bytes"),
        [
            (
                {"threshold": 2},
                bytes.fromhex("02"),
            )
        ],
    )
    def test_serialize(self, kwargs: dict[str, Any], expected_bytes: bytes):
        packet = LoginSetCompression(**kwargs)
        assert packet.serialize().flush() == bytearray(expected_bytes)

    @pytest.mark.parametrize(
        ("input_bytes", "expected_args"),
        [
            (
                bytes.fromhex("02"),
                {"threshold": 2},
            )
        ],
    )
    def test_deserialize(self, input_bytes: bytes, expected_args: dict[str, Any]):
        packet = LoginSetCompression.deserialize(Buffer(input_bytes))
        for arg_name, val in expected_args.items():
            assert getattr(packet, arg_name) == val
