from fastapi import APIRouter, Depends, HTTPException, Header, Body
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.merchant import Merchant
from app.schemas.merchant import MerchantCreate, MerchantResponse
from app.core.security import generate_api_keys, hash_secret, verify_signature, NONCE_STORE
from datetime import datetime

from app.auth.merchant_auth import get_authenticated_merchant
import json

router = APIRouter(prefix="/v1/merchants", tags=["Merchants"])

# ---------------------------
# Merchant Registration
# ---------------------------
@router.post("/", response_model=MerchantResponse)
def register_merchant(payload: MerchantCreate, db: Session = Depends(get_db)):
    """
    Registers a new merchant and returns public & secret keys.
    The secret key is only returned once at registration.
    """
    public_key, secret_key = generate_api_keys()

    merchant = Merchant(
        name=payload.name,
        public_key=public_key,
        secret_key_hash=hash_secret(secret_key),
        secret_key_plain=secret_key,  # demo only: store plaintext secret
        ip_whitelist=payload.ip_whitelist,
    )

    db.add(merchant)
    db.commit()
    db.refresh(merchant)

    # ⚠️ Secret key returned ONCE
    return {
        "id": merchant.id,
        "name": merchant.name,
        "status": merchant.status,
        "public_key": merchant.public_key,
        "created_at": merchant.created_at,
        "secret_key": secret_key,
    }

# ---------------------------
# Current Merchant Info
# ---------------------------
@router.get("/me")
def get_current_merchant(merchant=Depends(get_authenticated_merchant)):
    """
    Returns info about the currently authenticated merchant.
    """
    return {
        "id": merchant.id,
        "name": merchant.name,
        "status": merchant.status,
    }

# ---------------------------
# Secure HMAC Test Endpoint
# ---------------------------
@router.post("/secure-test")
def secure_test(
    payload: dict = Body(...),
    x_signature: str = Header(..., alias="X-Signature"),
    x_timestamp: int = Header(..., alias="X-Timestamp"),
    x_nonce: str = Header(..., alias="X-Nonce"),
    merchant=Depends(get_authenticated_merchant),
):
    """
    Test endpoint to verify HMAC-signed requests from merchants.
    Expects JSON payload in the request body.
    """
    # Convert payload dict to JSON string for signature verification
    payload_json = json.dumps(payload, separators=(",", ":"))

    # ✅ Use the actual secret stored at registration
    secret = merchant.secret_key_plain

    # Verify signature, timestamp, and nonce
    verify_signature(payload_json, x_signature, secret, x_timestamp, x_nonce)

    return {"status": "ok", "payload": payload}
