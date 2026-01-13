from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.transaction import Transaction, TransactionStatus
from app.schemas.transaction import TransactionCreate, TransactionResponse
from app.auth.merchant_auth import get_authenticated_merchant

router = APIRouter(prefix="/v1/transactions", tags=["Transactions"])


def mask_card(card_number: str) -> str:
    return "XXXX-XXXX-XXXX-" + card_number[-4:]


@router.post("/", response_model=TransactionResponse)
def create_transaction(
    payload: TransactionCreate,
    merchant=Depends(get_authenticated_merchant),
    db: Session = Depends(get_db),
):
    # Basic fraud checks
    if payload.amount > 10000:  # arbitrary max for demo
        raise HTTPException(status_code=400, detail="Amount exceeds allowed limit")

    transaction = Transaction(
        merchant_id=merchant.id,
        card_number_masked=mask_card(payload.card_number),
        amount=payload.amount,
        currency=payload.currency,
        status=TransactionStatus.initiated,
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    # Simulate authorization (simple random pass/fail)
    import random
    if random.random() > 0.1:
        transaction.status = TransactionStatus.authorized
    else:
        transaction.status = TransactionStatus.failed

    db.commit()
    db.refresh(transaction)

    return transaction
