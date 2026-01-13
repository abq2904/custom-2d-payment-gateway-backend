import uuid
from sqlalchemy import Column, String, DateTime, Enum, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class MerchantStatus(str, enum.Enum):
    active = "active"
    suspended = "suspended"


class Merchant(Base):
    __tablename__ = "merchants"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    name = Column(String, nullable=False)
    status = Column(
        Enum(MerchantStatus),
        default=MerchantStatus.active,
        nullable=False,
    )

    public_key = Column(String, unique=True, nullable=False)
    secret_key_hash = Column(String, nullable=False)
    secret_key_plain = Column(String, nullable=False)  # demo only, for HMAC testing

    ip_whitelist = Column(JSON, default=list)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
