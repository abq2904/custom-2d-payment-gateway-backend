from fastapi import FastAPI

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.database import engine, Base

from app.models import merchant  # noqa: F401 (ensures model registration)
from app.merchants.router import router as merchant_router


# Setup logging
setup_logging()

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
)

# Register routers
app.include_router(merchant_router)


# Health check
@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "environment": settings.app_env,
    }


# Create tables (DEV ONLY)
Base.metadata.create_all(bind=engine)


from app.transactions.router import router as transaction_router
app.include_router(transaction_router)
