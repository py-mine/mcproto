from __future__ import annotations

import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey, generate_private_key


def generate_shared_secret() -> bytes:  # pragma: no cover
    """Generate a random shared secret for client

    This secret will be sent to the server in :class:`~mcproto.packets.login.login.LoginEncryptionResponse` packet,
    and used to encrypt all future communication afterwards.

    This will be symetric encryption using AES/CFB8 stream cipher. And this shared secret will be 16-bytes long.
    """
    return os.urandom(16)


def generate_rsa_key() -> RSAPrivateKey:  # pragma: no cover
    """Generate a random RSA key pair for server.

    This key pair will be used for :class:`~mcproto.packets.login.login.LoginEncryptionRequest` packet,
    where the client will be sent the public part of this key pair, which will be used to encrypt the
    shared secret (and verification token) sent in :class:`~mcproto.packets.login.login.LoginEncryptionResponse`
    packet. The server will then use the private part of this key pair to decrypt that.

    This will be a 1024-bit RSA key pair.
    """
    return generate_private_key(public_exponent=65537, key_size=1024, backend=default_backend())


def encrypt_token_and_secret(
    public_key: RSAPublicKey,
    verification_token: bytes,
    shared_secret: bytes,
) -> tuple[bytes, bytes]:
    """Encrypts the verification token and shared secret with the server's public key.

    :param public_key: The RSA public key provided by the server
    :param verification_token: The verification token provided by the server
    :param shared_secret: The generated shared secret
    :return: A tuple containing (encrypted token, encrypted secret)
    """
    # Make absolutely certain that we're using bytes, not say bytearrays
    # this is needed since the cryptography lib calls some C code in the back
    # which relies on these being bytes
    if type(verification_token) is not bytes:
        verification_token = bytes(verification_token)
    if type(shared_secret) is not bytes:
        shared_secret = bytes(shared_secret)

    encrypted_token = public_key.encrypt(verification_token, PKCS1v15())
    encrypted_secret = public_key.encrypt(shared_secret, PKCS1v15())
    return encrypted_token, encrypted_secret
