"""Ask Sarthi endpoints."""

import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.entities import ChatMessage, Feedback
from app.schemas.contracts import ChatRequest, ChatResponse, FeedbackRequest
from app.services import chat as chat_service
from app.services.rate_limit import limiter

router = APIRouter()
log = logging.getLogger(__name__)


@router.post("/chat", response_model=ChatResponse)
@limiter.limit("20/minute")
def post_chat(
    request: Request,  # required by slowapi to identify the caller
    payload: ChatRequest,
    db: Session = Depends(get_db),
) -> ChatResponse:
    """Answer a question from the BIS corpus.

    Always returns 200 with a usable body — retrieval misses and model outages are represented
    as a low-confidence answer plus `warnings`, not as an error the UI has to special-case.
    """
    try:
        return chat_service.answer(db, payload)
    except Exception:
        db.rollback()
        log.exception("Unhandled error answering chat")
        raise HTTPException(status_code=500, detail="Could not process that question.")


@router.get("/chat/{session_id}/history")
def get_history(session_id: str, db: Session = Depends(get_db)) -> dict:
    """Replay a conversation, for reload-persistence in the UI."""
    rows = (
        db.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.id)
        )
        .scalars()
        .all()
    )
    import json

    return {
        "session_id": session_id,
        "messages": [
            {
                "message_id": m.id,
                "role": m.role,
                "content": m.content,
                "intent": m.intent,
                "confidence": m.confidence,
                "citations": json.loads(m.citations_json) if m.citations_json else [],
                "created_at": m.created_at.isoformat() if m.created_at else None,
            }
            for m in rows
        ],
    }


@router.post("/feedback")
def post_feedback(payload: FeedbackRequest, db: Session = Depends(get_db)) -> dict:
    if payload.message_id is not None and db.get(ChatMessage, payload.message_id) is None:
        raise HTTPException(status_code=404, detail="Unknown message_id")

    db.add(
        Feedback(
            message_id=payload.message_id,
            is_helpful=payload.is_helpful,
            reason=payload.reason,
        )
    )
    db.commit()
    return {"status": "recorded"}
