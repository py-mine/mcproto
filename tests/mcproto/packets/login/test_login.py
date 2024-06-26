from __future__ import annotations

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
from mcproto.packets.packet import InvalidPacketContentError
from mcproto.types.chat import JSONTextComponent
from mcproto.types.uuid import UUID
from tests.helpers import gen_serializable_test
from tests.mcproto.test_encryption import RSA_PUBLIC_KEY

# LoginStart
gen_serializable_test(
    context=globals(),
    cls=LoginStart,
    fields=[("username", str), ("uuid", UUID)],
    serialize_deserialize=[
        (
            ("ItsDrike", UUID("f70b4a42c9a04ffb92a31390c128a1b2")),
            bytes.fromhex("084974734472696b65f70b4a42c9a04ffb92a31390c128a1b2"),
        ),
        (
            ("foobar1", UUID("7a82476416fc4e8b8686a99c775db7d3")),
            bytes.fromhex("07666f6f626172317a82476416fc4e8b8686a99c775db7d3"),
        ),
    ],
)

# LoginEncryptionRequest
gen_serializable_test(
    context=globals(),
    cls=LoginEncryptionRequest,
    fields=[("server_id", str), ("public_key", bytes), ("verify_token", bytes)],
    serialize_deserialize=[
        (
            ("a" * 20, RSA_PUBLIC_KEY, bytes.fromhex("9bd416ef")),
            bytes.fromhex(
                "146161616161616161616161616161616161616161a20130819f300d06092a864886f70d010101050003818d003081890"
                "2818100cb515109911ea3e4740d8a17a7ccd9cf226c83c7615e4a5505cd124571ee210a4ba26c7c42e15f51fcb7fa90dc"
                "e6f83ebe0e163817c7d9fb1af7d981e90da2cc06ea59d01ff9fbb76b1803a0fe5af4a2c75145d89eb03e6a4aae21d2e7d"
                "4c3938a298da575e12e0ae178d61a69bc0ea0b381790f182d9dba715bfb503c99d92b0203010001049bd416ef"
            ),
        ),
    ],
    deserialization_fail=[
        (bytes.fromhex("14"), InvalidPacketContentError),
    ],
)


def test_login_encryption_request_noid():
    """Test LoginEncryptionRequest without server_id."""
    packet = LoginEncryptionRequest(public_key=RSA_PUBLIC_KEY, verify_token=bytes.fromhex("9bd416ef"))
    assert packet.server_id == " " * 20  # None is converted to an empty server id


# TestLoginEncryptionResponse
gen_serializable_test(
    context=globals(),
    cls=LoginEncryptionResponse,
    fields=[("shared_secret", bytes), ("verify_token", bytes)],
    serialize_deserialize=[
        (
            (b"I'm shared", b"Token"),
            bytes.fromhex("0a49276d2073686172656405546f6b656e"),
        ),
    ],
)


# LoginSuccess
gen_serializable_test(
    context=globals(),
    cls=LoginSuccess,
    fields=[("uuid", UUID), ("username", str)],
    serialize_deserialize=[
        (
            (UUID("f70b4a42c9a04ffb92a31390c128a1b2"), "Mario"),
            bytes.fromhex("f70b4a42c9a04ffb92a31390c128a1b2054d6172696f"),
        ),
    ],
)

# LoginDisconnect
gen_serializable_test(
    context=globals(),
    cls=LoginDisconnect,
    fields=[("reason", JSONTextComponent)],
    serialize_deserialize=[
        (
            (JSONTextComponent("You are banned."),),
            bytes.fromhex("1122596f75206172652062616e6e65642e22"),
        ),
    ],
)


# LoginPluginRequest
gen_serializable_test(
    context=globals(),
    cls=LoginPluginRequest,
    fields=[("message_id", int), ("channel", str), ("data", bytes)],
    serialize_deserialize=[
        (
            (0, "xyz", b"Hello"),
            bytes.fromhex("000378797a48656c6c6f"),
        ),
    ],
)


# LoginPluginResponse
gen_serializable_test(
    context=globals(),
    cls=LoginPluginResponse,
    fields=[("message_id", int), ("data", bytes)],
    serialize_deserialize=[
        (
            (0, b"Hello"),
            bytes.fromhex("000148656c6c6f"),
        ),
    ],
)

# LoginSetCompression
gen_serializable_test(
    context=globals(),
    cls=LoginSetCompression,
    fields=[("threshold", int)],
    serialize_deserialize=[
        (
            (2,),
            bytes.fromhex("02"),
        ),
    ],
)
