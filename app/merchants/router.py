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
