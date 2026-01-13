import secrets
import hashlib


def generate_api_keys():
    public_key = f"pk_{secrets.token_hex(16)}"
    secret_key = f"sk_{secrets.token_hex(32)}"
    return public_key, secret_key


def hash_secret(secret: str) -> str:
    return hashlib.sha256(secret.encode()).hexdigest()


import hmac
import time
from hashlib import sha256
from fastapi import HTTPException

# Nonce store for dev (in-memory). Replace with Redis in prod
NONCE_STORE = set()


def verify_signature(
    payload: str,
    signature: str,
    secret: str,
    timestamp: int,
    nonce: str,
    window: int = 300,
):
    """
    Verifies HMAC signature and prevents replay attacks.
    """
    # Check timestamp (seconds)
    now = int(time.time())
    if abs(now - timestamp) > window:
        raise HTTPException(status_code=400, detail="Request timestamp expired")

    # Replay protection
    if nonce in NONCE_STORE:
        raise HTTPException(status_code=400, detail="Replay attack detected")
    NONCE_STORE.add(nonce)

    # HMAC verification
    computed = hmac.new(secret.encode(), payload.encode(), sha256).hexdigest()
    if not hmac.compare_digest(computed, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")
