from typing import cast

from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
from cryptography.hazmat.primitives.serialization import load_pem_private_key

from mcproto.encryption import encrypt_token_and_secret

_SERIALIZED_RSA_PRIVATE_KEY = b"""
-----BEGIN PRIVATE KEY-----
MIICdgIBADANBgkqhkiG9w0BAQEFAASCAmAwggJcAgEAAoGBAMtRUQmRHqPkdA2K
F6fM2c8ibIPHYV5KVQXNEkVx7iEKS6JsfELhX1H8t/qQ3Ob4Pr4OFjgXx9n7GvfZ
gekNoswG6lnQH/n7t2sYA 6D+WvSix1FF2J6wPmpKriHS59TDk4opjaV14S4K4XjW
Gmm8DqCzgXkPGC2dunFb+1A8mdkrAgMBAAECgYAWj2dWkGu989OMzQ3i6LAic8dm
t/Dt7YGRqzejzQiHUgUieLcxFKDnEAu6GejpGBKeNCHzB3B9l4deiRwJKCIwHqMN
LKMKoayinA8mj/Y/ O/ELDofkEyeXOhFyM642sPpaxQJoNWc9QEsYbxpG2zeB3sPf
l3eIhkYTKVdxB+o8AQJBAPiddMjU8fuHyjKT6VCL2ZQbwnrRe1AaLLE6VLwEZuZC
wlbx5Lcszi77PkMRTvltQW39VN6MEjiYFSPtRJleA+sCQQDRW2e3BX6uiil2IZ08
tPFMnltFJpa 8YvW50N6mySd8Zg1oQJpzP2fC0n0+K4j3EiA/Zli8jBt45cJ4dMGX
km/BAkEAtkYy5j+BvolbDGP3Ti+KcRU9K/DD+QGHvNRoZYTQsIdHlpk4t7eo3zci
+ecJwMOCkhKHE7cccNPHxBRkFBGiywJAJBt2pMsu0R2FDxm3C6xNXaCGL0P7hVwv
8y9B51 QUGlFjiJJz0OKjm6c/8IQDqFEY/LZDIamsZ0qBItNIPEMGQQJALZV0GD5Y
zmnkw1hek/JcfQBlVYo3gFmWBh6Hl1Lb7p3TKUViJCA1k2f0aGv7+d9aFS0fRq6u
/sETkem8Jc1s3g==
-----END PRIVATE KEY-----
"""
RSA_PRIVATE_KEY = cast(RSAPrivateKey, load_pem_private_key(_SERIALIZED_RSA_PRIVATE_KEY, password=None))
RSA_PUBLIC_KEY = RSA_PRIVATE_KEY.public_key()


def test_encrypt_token_and_secret():
    verification_token = bytes.fromhex("9bd416ef")
    shared_secret = bytes.fromhex("f71e3033d4c0fc6aadee4417831b5c3e")

    encrypted_token, encrypted_secret = encrypt_token_and_secret(RSA_PUBLIC_KEY, verification_token, shared_secret)

    assert RSA_PRIVATE_KEY.decrypt(encrypted_token, PKCS1v15()) == verification_token
    assert RSA_PRIVATE_KEY.decrypt(encrypted_secret, PKCS1v15()) == shared_secret
