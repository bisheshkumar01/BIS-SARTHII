"""The guarantees that make this assistant safe to ship.

These tests are about *grounding*, not about answer quality: a compliance tool that invents an
IS number is worse than one that says "I don't know". Each test pins one rule in chat.answer().
"""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.session import Base
from app.models.entities import Chunk, Document
from app.schemas.contracts import ChatRequest, Confidence, Intent
from app.services import chat as chat_service
from app.services import llm, retrieval


@pytest.fixture()
def db():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()

    doc = Document(
        title="ISI Mark - Scheme I product certification",
        source_url="https://www.bis.gov.in/product-certification/",
        doc_type="scheme",
        verified=True,
    )
    session.add(doc)
    session.flush()
    session.add(
        Chunk(
            document_id=doc.id,
            heading="What Scheme I covers",
            content=(
                "The ISI mark is granted under Scheme I of Schedule II of the BIS "
                "(Conformity Assessment) Regulations, 2018. A licence is granted for a "
                "specific product manufactured to a specific Indian Standard at a specific "
                "factory address."
            ),
        )
    )
    session.commit()

    retrieval.invalidate()
    yield session
    session.close()
    retrieval.invalidate()


def _ask(db, message: str, language: str = "en"):
    return chat_service.answer(db, ChatRequest(session_id="s1", message=message, language=language))


def _stub_llm(monkeypatch, payload: dict):
    monkeypatch.setattr(llm, "is_available", lambda: True)
    monkeypatch.setattr(llm, "generate_json", lambda **kw: payload)


def test_offtopic_question_refuses_without_calling_the_model(db, monkeypatch):
    """Gate 1: below the relevance threshold, the model is never invoked at all."""
    called = False

    def explode(**kwargs):
        nonlocal called
        called = True
        raise AssertionError("the model must not be called for an off-topic question")

    monkeypatch.setattr(llm, "is_available", lambda: True)
    monkeypatch.setattr(llm, "generate_json", explode)

    res = _ask(db, "What is the best pizza in Naples?")

    assert called is False
    assert res.intent is Intent.OUT_OF_SCOPE
    assert res.confidence is Confidence.UNVERIFIED
    assert res.citations == []


def test_hallucinated_citation_ids_are_dropped(db, monkeypatch):
    """A chunk id the model invented was never retrieved, so it must not reach the UI."""
    _stub_llm(
        monkeypatch,
        {
            "answer": "The ISI mark is granted under Scheme I.",
            "intent": "process_howto",
            "confidence": "high",
            "used_chunk_ids": [1, 9999],  # 9999 does not exist
            "next_steps": [],
            "related_questions": [],
        },
    )

    res = _ask(db, "How does the ISI mark scheme work?")

    assert [c.chunk_id for c in res.citations] == [1]
    assert all(c.source_url.startswith("https://www.bis.gov.in") for c in res.citations)


def test_answer_citing_nothing_is_downgraded_to_unverified(db, monkeypatch):
    """Gate 3: a confident-sounding answer with no source is not allowed to claim confidence."""
    _stub_llm(
        monkeypatch,
        {
            "answer": "Every product in India requires an ISI mark.",  # unsupported claim
            "intent": "certification_required",
            "confidence": "high",
            "used_chunk_ids": [],
            "next_steps": [],
            "related_questions": [],
        },
    )

    res = _ask(db, "How does the ISI mark scheme work?")

    assert res.confidence is Confidence.UNVERIFIED
    assert res.citations == []
    assert any("not tied to a specific source" in w for w in res.warnings)


def test_citation_fields_come_from_the_database_not_the_model(db, monkeypatch):
    """Citations are rebuilt from stored rows, so the model cannot forge a title or URL."""
    _stub_llm(
        monkeypatch,
        {
            "answer": "See the scheme description.",
            "intent": "process_howto",
            "confidence": "high",
            "used_chunk_ids": [1],
            "next_steps": [],
            "related_questions": [],
        },
    )

    res = _ask(db, "How does the ISI mark scheme work?")
    cite = res.citations[0]

    assert cite.document_title == "ISI Mark - Scheme I product certification"
    assert cite.source_url == "https://www.bis.gov.in/product-certification/"
    assert cite.heading == "What Scheme I covers"
    assert cite.snippet in db.get(Chunk, 1).content or db.get(Chunk, 1).content.startswith(
        cite.snippet.rstrip("…")
    )


def test_unverified_source_caps_confidence(db, monkeypatch):
    """Gate 4: a corpus entry no human has checked cannot yield a high-confidence answer."""
    doc = db.get(Document, 1)
    doc.verified = False
    db.commit()

    _stub_llm(
        monkeypatch,
        {
            "answer": "The ISI mark is granted under Scheme I.",
            "intent": "process_howto",
            "confidence": "high",
            "used_chunk_ids": [1],
            "next_steps": [],
            "related_questions": [],
        },
    )

    res = _ask(db, "How does the ISI mark scheme work?")

    assert res.confidence is Confidence.LOW
    assert any("not yet been verified" in w for w in res.warnings)


def test_model_outage_still_returns_the_source_text(db, monkeypatch):
    """An API failure degrades to showing the retrieved passage, never to a 500."""
    monkeypatch.setattr(llm, "is_available", lambda: True)

    def boom(**kwargs):
        raise llm.LLMError("quota exhausted")

    monkeypatch.setattr(llm, "generate_json", boom)

    res = _ask(db, "How does the ISI mark scheme work?")

    assert res.answer  # something useful came back
    assert res.citations, "the retrieved source should still be cited"
    assert any("could not generate an answer" in w for w in res.warnings)


def test_conversation_is_persisted(db, monkeypatch):
    _stub_llm(
        monkeypatch,
        {
            "answer": "Scheme I covers the ISI mark.",
            "intent": "process_howto",
            "confidence": "medium",
            "used_chunk_ids": [1],
            "next_steps": ["Register on the BIS portal."],
            "related_questions": [],
        },
    )

    res = _ask(db, "How does the ISI mark scheme work?")

    from app.models.entities import ChatMessage

    rows = db.query(ChatMessage).order_by(ChatMessage.id).all()
    assert [r.role for r in rows] == ["user", "assistant"]
    assert res.message_id == rows[1].id
    assert res.next_steps == ["Register on the BIS portal."]


def test_hindi_question_retrieves_from_the_english_corpus(db, monkeypatch):
    """Hindi must reach the corpus.

    Two bugs made this fail before: the tokenizer's [a-z0-9]+ dropped every Devanagari
    character, and out-of-vocabulary terms inflated the score ceiling so a correct top hit
    scored below the refusal threshold.
    """
    captured = {}

    def capture(**kwargs):
        captured["prompt"] = kwargs["prompt"]
        return {
            "answer": "ISI मार्क योजना I के अंतर्गत दिया जाता है।",
            "intent": "process_howto",
            "confidence": "medium",
            "used_chunk_ids": [1],
            "next_steps": [],
            "related_questions": [],
        }

    monkeypatch.setattr(llm, "is_available", lambda: True)
    monkeypatch.setattr(llm, "generate_json", capture)

    res = _ask(db, "ISI मार्क के लिए लाइसेंस और प्रमाणन प्रक्रिया क्या है?", language="hi")

    assert res.intent is not Intent.OUT_OF_SCOPE, "Hindi question was wrongly refused"
    assert res.citations, "Hindi question retrieved nothing"
    assert "Hindi" in captured["prompt"]


def test_unmatchable_terms_do_not_deflate_the_score():
    """A word the corpus has never seen must not dilute the relevance of one it has."""
    from app.services.retrieval import _Bm25Index, _Entry, tokenize

    def entry(cid: int, text: str) -> _Entry:
        toks = tokenize(text)
        tf: dict[str, int] = {}
        for t in toks:
            tf[t] = tf.get(t, 0) + 1
        return _Entry(cid, "doc", None, None, text, "https://example.test", toks, tf, len(toks))

    index = _Bm25Index(
        [
            entry(1, "hallmarking of gold jewellery requires jeweller registration"),
            entry(2, "packaged drinking water requires a licence before sale"),
        ]
    )

    clean = index.search("hallmarking gold jewellery", 1)[0].score
    padded = index.search("hallmarking gold jewellery zzzqqq wwwxxx yyyvvv", 1)[0].score

    assert clean == padded, "out-of-vocabulary padding changed the score"
