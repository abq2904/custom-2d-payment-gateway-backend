from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.merchant import Merchant
from app.schemas.merchant import MerchantCreate, MerchantResponse
from app.core.security import generate_api_keys, hash_secret

router = APIRouter(prefix="/v1/merchants", tags=["Merchants"])


@router.post("/", response_model=MerchantResponse)
def register_merchant(payload: MerchantCreate, db: Session = Depends(get_db)):
    public_key, secret_key = generate_api_keys()

    merchant = Merchant(
        name=payload.name,
        public_key=public_key,
        secret_key_hash=hash_secret(secret_key),
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

from app.auth.merchant_auth import get_authenticated_merchant


@router.get("/me")
def get_current_merchant(
    merchant=Depends(get_authenticated_merchant),
):
    return {
        "id": merchant.id,
        "name": merchant.name,
        "status": merchant.status,
    }

from fastapi import Header
from app.core.security import verify_signature, NONCE_STORE, hash_secret
from datetime import datetime
from sqlalchemy.orm import Session
from app.core.database import get_db

@router.post("/secure-test")
def secure_test(
    payload: str,
    x_signature: str = Header(..., alias="X-Signature"),
    x_timestamp: int = Header(..., alias="X-Timestamp"),
    x_nonce: str = Header(..., alias="X-Nonce"),
    merchant=Depends(get_authenticated_merchant),
):
    # Verify signature
    secret_hash = merchant.secret_key_hash
    # In a real system, we would store the plaintext once to generate signature
    # For dev, we simulate using same secret returned at registration
    secret = "USE_THE_SECRET_KEY_RETURNED_AT_REGISTRATION"  # placeholder
    verify_signature(payload, x_signature, secret, x_timestamp, x_nonce)

    return {"status": "ok", "payload": payload}
