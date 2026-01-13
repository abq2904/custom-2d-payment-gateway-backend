import secrets
import hashlib


def generate_api_keys():
    public_key = f"pk_{secrets.token_hex(16)}"
    secret_key = f"sk_{secrets.token_hex(32)}"
    return public_key, secret_key


def hash_secret(secret: str) -> str:
    return hashlib.sha256(secret.encode()).hexdigest()
