"""BIS SARTHI API entrypoint.

Run from the backend/ directory:
    uvicorn app.main:app --reload
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.config import settings
from app.db.session import Base, engine
from app.models import entities  # noqa: F401  — registers tables on Base
from app.routers import chat, health
from app.services.rate_limit import limiter

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s | %(message)s"
)

app = FastAPI(
    title="BIS SARTHI API",
    description="AI-powered Indian Standards and BIS compliance assistant (SIH26107)",
    version="0.1.0",
)

app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)


@app.exception_handler(RateLimitExceeded)
def on_rate_limit(request, exc):
    """Answer in the response shape the chat UI already renders, so it needs no special case."""
    from fastapi.responses import JSONResponse

    return JSONResponse(
        status_code=429,
        content={"detail": "Too many questions in a short time. Wait a minute and try again."},
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(chat.router, prefix="/api", tags=["chat"])


@app.on_event("startup")
def on_startup() -> None:
    """Create tables, ensure the corpus exists, and make the writable dirs.

    Alembic is overkill for a one-week MVP. The seeding step matters on serverless: /tmp is
    wiped between cold starts, so without it a fresh instance would answer every question
    with "no source found".
    """
    log = logging.getLogger(__name__)

    Base.metadata.create_all(bind=engine)

    # Read-only deployment filesystem: only the /tmp redirect is creatable.
    for path in (settings.writable_upload_dir, settings.faiss_index_path):
        try:
            path.mkdir(parents=True, exist_ok=True)
        except OSError:
            log.warning("Could not create %s (read-only filesystem) — continuing", path)

    from app.db.session import SessionLocal
    from app.services.seed import ensure_seeded

    db = SessionLocal()
    try:
        ensure_seeded(db)
    finally:
        db.close()

    log.info("BIS SARTHI API ready (serverless=%s)", settings.is_serverless)
