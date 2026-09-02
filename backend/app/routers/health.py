"""Health endpoint. Also reports which subsystems are wired, so demo-day checks are one call."""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import settings
from app.db.session import get_db

router = APIRouter()


@router.get("/health")
def health(db: Session = Depends(get_db)) -> dict:
    try:
        db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False

    index_files = list(settings.faiss_index_path.glob("*.faiss"))

    return {
        "status": "ok" if db_ok else "degraded",
        "database": db_ok,
        "llm_provider": settings.llm_provider,
        "llm_key_configured": settings.has_llm_key,
        "mock_llm": settings.mock_llm,
        "faiss_index_built": len(index_files) > 0,
    }
