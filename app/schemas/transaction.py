from pydantic import BaseModel, condecimal
from uuid import UUID
from datetime import datetime
from app.models.transaction import TransactionStatus
from typing import Optional


class TransactionCreate(BaseModel):
    card_number: str
    amount: condecimal(gt=0)
    currency: Optional[str] = "USD"


class TransactionResponse(BaseModel):
    id: UUID
    merchant_id: UUID
    card_number_masked: str
    amount: condecimal(gt=0)
    currency: str
    status: TransactionStatus
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
