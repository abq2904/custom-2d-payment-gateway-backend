from fastapi import Header, HTTPException, Request, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.merchant import Merchant, MerchantStatus


def get_authenticated_merchant(
    request: Request,
    x_public_key: str = Header(..., alias="X-Public-Key"),
    db: Session = Depends(get_db),
) -> Merchant:
    merchant = (
        db.query(Merchant)
        .filter(Merchant.public_key == x_public_key)
        .first()
    )

    if not merchant:
        raise HTTPException(status_code=401, detail="Invalid API key")

    if merchant.status != MerchantStatus.active:
        raise HTTPException(status_code=403, detail="Merchant suspended")

    client_ip = request.client.host
    if merchant.ip_whitelist and client_ip not in merchant.ip_whitelist:
        raise HTTPException(status_code=403, detail="IP not allowed")

    return merchant
