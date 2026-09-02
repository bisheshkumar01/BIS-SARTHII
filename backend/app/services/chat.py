"""Grounded answer generation for Ask Sarthi.

The one rule this module exists to enforce: **the model never supplies facts, only wording.**

    retrieve -> if nothing clears the threshold, refuse without calling the model
             -> otherwise hand the model the retrieved text and make it cite by chunk id
             -> keep only citations whose ids were actually retrieved

A citation the model invents is dropped, not rendered. An answer with no surviving citation is
downgraded to `unverified` and carries a warning, because an uncited claim about compliance is
exactly the failure mode this product cannot have.
"""

from __future__ import annotations

import json
import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.models.entities import ChatMessage, ChatSession, Document
from app.schemas.contracts import (
    ChatRequest,
    ChatResponse,
    Citation,
    Confidence,
    Intent,
)
from app.services import llm, retrieval

log = logging.getLogger(__name__)

MAX_SNIPPET = 400
HISTORY_TURNS = 6

SYSTEM_INSTRUCTION = """\
You are Sarthi, a compliance guide for the Bureau of Indian Standards (BIS).

You answer ONLY from the numbered SOURCES supplied in each request. This is absolute:

- Never state an IS number, form name, fee, timeline, or legal requirement that is not written \
in the sources. If a user asks for one and it is not there, say you do not have a source for it.
- Never guess which standard applies to a product. If the sources do not name it, explain how \
to narrow it down and say the exact number must be confirmed against the BIS catalogue.
- Cite every factual sentence by putting the source's id in `used_chunk_ids`. Only ids from \
the SOURCES block are valid.
- If the sources do not answer the question, set intent to "out_of_scope", confidence to \
"unverified", and say plainly what you cannot confirm. A refusal is a correct answer here.

Distinguish clearly between certification that is MANDATORY (a Quality Control Order or the \
CRS covers the product) and VOLUNTARY (everything else). Never imply a product is mandatory \
unless a source says so.

Tone: direct and practical, for a small manufacturer who is not a lawyer. Short paragraphs. \
No preamble, no marketing. Do not open with "Great question".

`confidence`:
- "high"   - sources directly and completely answer the question.
- "medium" - sources answer it partly, or you had to generalise.
- "low"    - sources are only tangentially related.
- "unverified" - you could not answer from the sources.

Answer in the language named in the request. For Hindi, use natural Hindi but keep IS numbers, \
form codes and scheme names (ISI, CRS, FMCS, BIS) in their standard form.
"""

RESPONSE_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "answer": {
            "type": "STRING",
            "description": "The reply to the user, grounded in the sources.",
        },
        "intent": {
            "type": "STRING",
            "enum": [i.value for i in Intent],
        },
        "confidence": {
            "type": "STRING",
            "enum": [c.value for c in Confidence],
        },
        "used_chunk_ids": {
            "type": "ARRAY",
            "items": {"type": "INTEGER"},
            "description": "Ids of the sources this answer actually relied on.",
        },
        "next_steps": {
            "type": "ARRAY",
            "items": {"type": "STRING"},
            "description": "Up to 4 concrete actions the user can take next.",
        },
        "related_questions": {
            "type": "ARRAY",
            "items": {"type": "STRING"},
            "description": "Up to 3 follow-up questions answerable from BIS sources.",
        },
    },
    "required": ["answer", "intent", "confidence", "used_chunk_ids"],
}

REFUSAL_EN = (
    "I don't have a BIS source covering that, so I can't answer it reliably.\n\n"
    "I can help with: which standard applies to a product, whether certification is "
    "mandatory or voluntary, how the ISI mark, CRS, FMCS and hallmarking schemes work, "
    "and what the application process involves.\n\n"
    "If your question is about a specific product, tell me what it is made of and what "
    "it is used for, and I'll narrow it down from the sources I do have."
)

REFUSAL_HI = (
    "इस विषय पर मेरे पास कोई BIS स्रोत नहीं है, इसलिए मैं विश्वसनीय उत्तर नहीं दे सकता।\n\n"
    "मैं इनमें मदद कर सकता हूँ: किसी उत्पाद पर कौन-सा मानक लागू होता है, प्रमाणन अनिवार्य है "
    "या स्वैच्छिक, ISI मार्क / CRS / FMCS / हॉलमार्किंग योजनाएँ कैसे काम करती हैं, और आवेदन "
    "प्रक्रिया क्या है।\n\n"
    "यदि प्रश्न किसी विशेष उत्पाद के बारे में है, तो बताइए वह किस सामग्री का है और किस काम "
    "आता है।"
)

DISCLAIMER_EN = (
    "This is guidance from published BIS sources, not legal advice. "
    "Confirm anything you act on against the linked official source."
)
DISCLAIMER_HI = (
    "यह प्रकाशित BIS स्रोतों पर आधारित मार्गदर्शन है, कानूनी सलाह नहीं। "
    "कार्रवाई से पहले आधिकारिक स्रोत से पुष्टि करें।"
)


def _snippet(text: str) -> str:
    """Trim to a renderable length on a word boundary — the Evidence Panel shows this verbatim."""
    if len(text) <= MAX_SNIPPET:
        return text
    cut = text[:MAX_SNIPPET].rsplit(" ", 1)[0]
    return cut + "…"


def _get_or_create_session(db: Session, session_id: str, language: str) -> ChatSession:
    session = db.get(ChatSession, session_id)
    if session is None:
        session = ChatSession(id=session_id, language=language)
        db.add(session)
        db.flush()
    return session


def _history(db: Session, session_id: str) -> str:
    """Recent turns, so follow-ups like "and what about imports?" resolve."""
    rows = (
        db.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.id.desc())
            .limit(HISTORY_TURNS)
        )
        .scalars()
        .all()
    )
    if not rows:
        return ""
    lines = [
        f"{'User' if m.role == 'user' else 'Sarthi'}: {m.content}" for m in reversed(rows)
    ]
    return "\n".join(lines)


def _build_prompt(message: str, hits: list[retrieval.Hit], history: str, language: str) -> str:
    blocks = []
    for h in hits:
        header = f"[{h.chunk_id}] {h.document_title}"
        if h.heading:
            header += f" — {h.heading}"
        blocks.append(f"{header}\nURL: {h.source_url}\n{h.content}")
    sources = "\n\n".join(blocks)

    parts = []
    if history:
        parts.append(f"CONVERSATION SO FAR:\n{history}\n")
    parts.append(f"SOURCES:\n{sources}\n")
    parts.append(
        f"USER QUESTION ({'Hindi' if language == 'hi' else 'English'}): {message}\n\n"
        f"Answer from the sources above. Put the id of every source you relied on in "
        f"used_chunk_ids. Reply in {'Hindi' if language == 'hi' else 'English'}."
    )
    return "\n".join(parts)


def _mock_answer(hits: list[retrieval.Hit], language: str) -> dict:
    """Deterministic stand-in for MOCK_LLM=1. Quotes real retrieved text, so the Evidence
    Panel still shows something true — it just isn't phrased by a model."""
    top = hits[0]
    lead = "उपलब्ध BIS स्रोत के अनुसार:" if language == "hi" else "From the BIS sources I have:"
    return {
        "answer": f"{lead}\n\n{_snippet(top.content)}\n\n(MOCK_LLM=1 — retrieval is live, "
        f"generation is stubbed.)",
        "intent": Intent.PROCESS_HOWTO.value,
        "confidence": Confidence.MEDIUM.value,
        "used_chunk_ids": [h.chunk_id for h in hits[:2]],
        "next_steps": ["Open the linked BIS source to confirm the details."],
        "related_questions": [],
    }


def answer(db: Session, req: ChatRequest) -> ChatResponse:
    language = "hi" if req.language == "hi" else "en"
    session = _get_or_create_session(db, req.session_id, language)

    db.add(ChatMessage(session_id=session.id, role="user", content=req.message))
    db.flush()

    warnings: list[str] = []
    hits = retrieval.search(db, req.message, settings.retrieval_top_k)
    top_hits = hits[: settings.rerank_top_n]

    # Gate 1 — nothing relevant retrieved. Refuse *without* calling the model, so there is no
    # opportunity for it to answer from parametric memory about Indian law.
    if not top_hits or top_hits[0].score < settings.relevance_threshold:
        log.info(
            "Below relevance threshold (best=%.3f < %.3f) — refusing without an LLM call",
            top_hits[0].score if top_hits else 0.0,
            settings.relevance_threshold,
        )
        return _persist(
            db,
            session,
            text=REFUSAL_HI if language == "hi" else REFUSAL_EN,
            intent=Intent.OUT_OF_SCOPE,
            confidence=Confidence.UNVERIFIED,
            citations=[],
            next_steps=[],
            related=[],
            warnings=warnings,
        )

    # Gate 2 — no way to generate. Better to show the retrieved source than to fail the request.
    if not llm.is_available():
        best = top_hits[0]
        warnings.append(
            "The language model is not configured, so this is the raw source text rather than "
            "a written answer. Set GEMINI_API_KEY in .env, or MOCK_LLM=1."
        )
        return _persist(
            db,
            session,
            text=_snippet(best.content),
            intent=Intent.EXPLAIN_STANDARD,
            confidence=Confidence.LOW,
            citations=_citations(db, top_hits, {best.chunk_id}),
            next_steps=[],
            related=[],
            warnings=warnings,
        )

    try:
        raw = llm.generate_json(
            system_instruction=SYSTEM_INSTRUCTION,
            prompt=_build_prompt(req.message, top_hits, _history(db, session.id), language),
            schema=RESPONSE_SCHEMA,
            mock_response=_mock_answer(top_hits, language),
        )
    except llm.LLMError as exc:
        log.error("Generation failed: %s", exc)
        best = top_hits[0]
        warnings.append(
            "The assistant could not generate an answer just now, so here is the most "
            "relevant source text instead."
        )
        return _persist(
            db,
            session,
            text=_snippet(best.content),
            intent=Intent.EXPLAIN_STANDARD,
            confidence=Confidence.LOW,
            citations=_citations(db, top_hits, {best.chunk_id}),
            next_steps=[],
            related=[],
            warnings=warnings,
        )

    # Keep only ids that were genuinely retrieved. A model-invented id is a hallucinated
    # citation; dropping it silently is the whole point of this step.
    retrieved_ids = {h.chunk_id for h in top_hits}
    claimed = {int(c) for c in raw.get("used_chunk_ids", []) if isinstance(c, (int, str)) and str(c).lstrip("-").isdigit()}
    used_ids = claimed & retrieved_ids
    if claimed - retrieved_ids:
        log.warning("Model cited unretrieved chunk ids: %s", sorted(claimed - retrieved_ids))

    intent = _coerce_intent(raw.get("intent"))
    confidence = _coerce_confidence(raw.get("confidence"))
    answer_text = (raw.get("answer") or "").strip()

    if not answer_text:
        answer_text = REFUSAL_HI if language == "hi" else REFUSAL_EN
        intent, confidence = Intent.OUT_OF_SCOPE, Confidence.UNVERIFIED

    citations = _citations(db, top_hits, used_ids)

    # Gate 3 — an answer that cites nothing cannot be trusted, whatever the model claimed.
    if not citations and intent is not Intent.OUT_OF_SCOPE:
        confidence = Confidence.UNVERIFIED
        warnings.append(
            "This answer is not tied to a specific source passage — treat it as a starting "
            "point and confirm it against bis.gov.in."
        )

    # Gate 4 — the corpus itself is not human-checked yet.
    if any(c.document_title for c in citations) and _has_unverified(db, used_ids):
        if confidence in (Confidence.HIGH, Confidence.MEDIUM):
            confidence = Confidence.LOW
        warnings.append(
            "Some cited passages have not yet been verified against the official BIS source."
        )

    if intent is not Intent.OUT_OF_SCOPE:
        warnings.append(DISCLAIMER_HI if language == "hi" else DISCLAIMER_EN)

    return _persist(
        db,
        session,
        text=answer_text,
        intent=intent,
        confidence=confidence,
        citations=citations,
        next_steps=[str(s) for s in (raw.get("next_steps") or [])][:4],
        related=[str(s) for s in (raw.get("related_questions") or [])][:3],
        warnings=warnings,
    )


def _has_unverified(db: Session, used_ids: set[int]) -> bool:
    if not used_ids:
        return False
    from app.models.entities import Chunk

    rows = db.execute(
        select(Document.verified)
        .join(Chunk, Chunk.document_id == Document.id)
        .where(Chunk.id.in_(used_ids))
    ).scalars().all()
    return any(v is False for v in rows)


def _citations(db: Session, hits: list[retrieval.Hit], used_ids: set[int]) -> list[Citation]:
    """Build citations from retrieved hits only. Every field comes from the database row."""
    return [
        Citation(
            chunk_id=h.chunk_id,
            document_title=h.document_title,
            heading=h.heading,
            page=h.page,
            snippet=_snippet(h.content),
            source_url=h.source_url,
            score=h.score,
        )
        for h in hits
        if h.chunk_id in used_ids
    ]


def _coerce_intent(value: object) -> Intent:
    try:
        return Intent(str(value))
    except ValueError:
        return Intent.PROCESS_HOWTO


def _coerce_confidence(value: object) -> Confidence:
    try:
        return Confidence(str(value))
    except ValueError:
        return Confidence.LOW


def _persist(
    db: Session,
    session: ChatSession,
    *,
    text: str,
    intent: Intent,
    confidence: Confidence,
    citations: list[Citation],
    next_steps: list[str],
    related: list[str],
    warnings: list[str],
) -> ChatResponse:
    row = ChatMessage(
        session_id=session.id,
        role="assistant",
        content=text,
        intent=intent.value,
        confidence=confidence.value,
        citations_json=json.dumps([c.model_dump() for c in citations]),
    )
    db.add(row)
    db.commit()
    db.refresh(row)

    return ChatResponse(
        session_id=session.id,
        message_id=row.id,
        answer=text,
        intent=intent,
        confidence=confidence,
        citations=citations,
        next_steps=next_steps,
        related_questions=related,
        warnings=warnings,
    )
