from __future__ import annotations

import os
from typing import cast

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from cryptography.hazmat.primitives.serialization import load_der_public_key


def generate_shared_secret() -> bytes:
    """Generate a random shared secret for client

    This secret will be sent to the server in :class:`~mcproto.packets.login.login.LoginEncryptionResponse` packet,
    and used to encrypt all future communication afterwards.

    This will be symetric encryption using AES/CFB8 stream cipher. And this shared secret will be 16-bytes long.
    """
    return os.urandom(16)


def encrypt_token_and_secret(
    public_key: bytes,
    verification_token: bytes,
    shared_secret: bytes,
) -> tuple[bytes, bytes]:
    """Encrypts the verification token and shared secret with the server's public key.

    :param public_key: The RSA public key provided by the server
    :param verification_token: The verification token provided by the server
    :param shared_secret: The generated shared secret
    :return: A tuple containing (encrypted token, encrypted secret)
    """
    # Key type is determined by the passed key itself, we know in our case, we'll be used
    # RSA keys so we explicitly type-cast here.
    pubkey = cast(RSAPublicKey, load_der_public_key(public_key, default_backend()))

    # Make absolutely certain that we're using bytes, not say bytearrays
    # this is needed since the cryptography lib calls some C code in the back
    # which relies on these being bytes
    if type(verification_token) is not bytes:
        verification_token = bytes(verification_token)
    if type(shared_secret) is not bytes:
        shared_secret = bytes(shared_secret)

    encrypted_token = pubkey.encrypt(verification_token, PKCS1v15())
    encrypted_secret = pubkey.encrypt(shared_secret, PKCS1v15())
    return encrypted_token, encrypted_secret
