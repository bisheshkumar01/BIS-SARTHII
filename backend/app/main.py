"""BIS SARTHI API entrypoint.

Run from the backend/ directory:
    uvicorn app.main:app --reload
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db.session import Base, engine
from app.models import entities  # noqa: F401  — registers tables on Base
from app.routers import health

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s | %(message)s"
)

app = FastAPI(
    title="BIS SARTHI API",
    description="AI-powered Indian Standards and BIS compliance assistant (SIH26107)",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api", tags=["health"])


@app.on_event("startup")
def on_startup() -> None:
    """Create tables and required directories. Alembic is overkill for a one-week MVP."""
    Base.metadata.create_all(bind=engine)
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    settings.faiss_index_path.mkdir(parents=True, exist_ok=True)
    logging.getLogger(__name__).info("BIS SARTHI API ready")
