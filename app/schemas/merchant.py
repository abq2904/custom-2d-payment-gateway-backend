from pydantic import BaseModel
from typing import List
from app.models.merchant import MerchantStatus
from uuid import UUID
from datetime import datetime


class MerchantCreate(BaseModel):
    name: str
    ip_whitelist: List[str] = []


class MerchantResponse(BaseModel):
    id: UUID
    name: str
    status: MerchantStatus
    public_key: str
    created_at: datetime

    class Config:
        from_attributes = True
