"""Lexical retrieval over the seed corpus.

BM25 in plain Python: no FAISS, no sentence-transformers, no model download. That keeps the
chat path runnable on a laptop and in CI. When the embedding index lands, replace `search()`
with a hybrid scorer — everything upstream depends only on its return type.
"""

from __future__ import annotations

import math
import re
import threading
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import Chunk, Document

# Devanagari (U+0900-U+097F) is matched explicitly: a plain [a-z0-9]+ silently drops every
# Hindi character, which made Hindi questions retrieve nothing at all.
_TOKEN = re.compile("[a-z0-9]+|[\u0900-\u097F]+")

# Common words plus BIS filler that appears in nearly every chunk. Terms this frequent carry
# no signal and, worse, let a vague question match everything with a middling score.
_STOPWORDS = frozenset(
    """
    a an and are as at be by do does for from has have how i in is it its my need of on or
    that the this to was what when where which who will with you your can should must if
    my me we our do i'm bis indian standard standards india
    """.split()
)


# The corpus is English, so a Hindi query shares no vocabulary with it and BM25 scores zero
# however well it is tokenised. This glossary expands the BIS terms a Hindi question actually
# uses into their English equivalents, which is enough to reach the right chunk.
#
# A stopgap, deliberately: the real fix is a multilingual embedding model, at which point the
# glossary goes away. Until then, an unmapped Hindi word is simply a term that does not match —
# the relevance gate catches that and refuses rather than answering badly.
_HI_EN = {
    "प्रमाणन": ["certification", "certificate"],
    "प्रमाणपत्र": ["certification", "licence"],
    "अनिवार्य": ["mandatory", "compulsory"],
    "स्वैच्छिक": ["voluntary"],
    "मानक": ["standard", "specification"],
    "लाइसेंस": ["licence", "license"],
    "पंजीकरण": ["registration", "register"],
    "आवेदन": ["application", "apply"],
    "प्रक्रिया": ["process", "procedure"],
    "शुल्क": ["fee", "fees"],
    "कारखाना": ["factory", "manufacturing"],
    "निर्माता": ["manufacturer"],
    "उत्पाद": ["product"],
    "आयात": ["import", "imported"],
    "निर्यात": ["export"],
    "परीक्षण": ["test", "testing", "laboratory"],
    "नमूना": ["sample", "samples"],
    "पेयजल": ["drinking", "water", "packaged"],
    "पानी": ["water"],
    "पैकेज्ड": ["packaged"],
    "खनिज": ["mineral"],
    "बल्ब": ["lamp", "led", "bulb"],
    "बिजली": ["electrical"],
    "उपकरण": ["appliance", "appliances"],
    "सोना": ["gold"],
    "आभूषण": ["jewellery", "hallmarking"],
    "हॉलमार्किंग": ["hallmarking", "gold"],
    "स्टील": ["steel", "stainless"],
    "इस्पात": ["steel"],
    "बोतल": ["bottle", "container"],
    "फॉर्म": ["form", "application"],
    "प्रपत्र": ["form", "application"],
    "योजना": ["scheme"],
    "गुणवत्ता": ["quality"],
    "सुरक्षा": ["safety"],
    "नवीनीकरण": ["renewal", "renew"],
    "विदेशी": ["foreign"],
}


def tokenize(text: str, *, expand: bool = False) -> list[str]:
    """Tokenise for BM25. `expand=True` adds English equivalents for Hindi query terms."""
    out: list[str] = []
    for t in _TOKEN.findall(text.lower()):
        if len(t) <= 1:
            continue
        if t in _STOPWORDS:
            continue
        out.append(t)
        if expand:
            out.extend(_HI_EN.get(t, ()))
    return out


@dataclass
class Hit:
    """One retrieved chunk with everything a Citation needs."""

    chunk_id: int
    document_title: str
    heading: str | None
    page: int | None
    content: str
    source_url: str
    score: float


@dataclass
class _Entry:
    chunk_id: int
    document_title: str
    heading: str | None
    page: int | None
    content: str
    source_url: str
    tokens: list[str]
    term_freq: dict[str, int]
    length: int


class _Bm25Index:
    """In-memory BM25. The seed corpus is a few dozen chunks, so a full rebuild is trivial."""

    K1 = 1.5
    B = 0.75

    def __init__(self, entries: list[_Entry]) -> None:
        self.entries = entries
        self.avg_len = (sum(e.length for e in entries) / len(entries)) if entries else 0.0
        doc_freq: dict[str, int] = {}
        for e in entries:
            for term in e.term_freq:
                doc_freq[term] = doc_freq.get(term, 0) + 1
        n = len(entries)
        # Standard BM25 IDF with the +1 that keeps it positive for terms in every document.
        self.idf = {
            term: math.log(1 + (n - df + 0.5) / (df + 0.5)) for term, df in doc_freq.items()
        }
        self.max_idf = max(self.idf.values(), default=1.0)

    def search(self, query: str, top_k: int) -> list[Hit]:
        q_terms = tokenize(query, expand=True)
        if not q_terms or not self.entries:
            return []

        # Ceiling for a perfect match: every *matchable* query term saturated in one chunk.
        # Dividing by it maps scores onto 0..1, which is what RELEVANCE_THRESHOLD is expressed
        # in — raw BM25 is unbounded and would make that threshold meaningless.
        #
        # Only terms present in the vocabulary count. A term the corpus has never seen cannot
        # contribute to the numerator, so charging the denominator for it punishes a query for
        # words it was never going to match: a Hindi question carries its Devanagari tokens
        # alongside the glossary's English ones and would score a third of its true relevance;
        # an English typo does the same on a smaller scale.
        matchable = {t for t in q_terms if t in self.idf}
        if not matchable:
            return []
        ceiling = sum(self.idf[t] for t in matchable) * (self.K1 + 1)
        if ceiling <= 0:
            return []

        scored: list[Hit] = []
        for e in self.entries:
            raw = 0.0
            for term in matchable:
                tf = e.term_freq.get(term)
                if not tf:
                    continue
                norm = 1 - self.B + self.B * (e.length / self.avg_len if self.avg_len else 1)
                raw += self.idf.get(term, 0.0) * (tf * (self.K1 + 1)) / (tf + self.K1 * norm)
            if raw <= 0:
                continue
            scored.append(
                Hit(
                    chunk_id=e.chunk_id,
                    document_title=e.document_title,
                    heading=e.heading,
                    page=e.page,
                    content=e.content,
                    source_url=e.source_url,
                    score=round(min(raw / ceiling, 1.0), 4),
                )
            )

        scored.sort(key=lambda h: h.score, reverse=True)
        return scored[:top_k]


_index: _Bm25Index | None = None
_lock = threading.Lock()


def _build(db: Session) -> _Bm25Index:
    rows = db.execute(
        select(Chunk, Document).join(Document, Chunk.document_id == Document.id)
    ).all()

    entries: list[_Entry] = []
    for chunk, doc in rows:
        # Heading and title are indexed alongside the body so a question phrased in the
        # vocabulary of a heading ("hallmarking", "CRS") still reaches the chunk.
        tokens = tokenize(f"{doc.title} {chunk.heading or ''} {chunk.content}")
        tf: dict[str, int] = {}
        for t in tokens:
            tf[t] = tf.get(t, 0) + 1
        entries.append(
            _Entry(
                chunk_id=chunk.id,
                document_title=doc.title,
                heading=chunk.heading,
                page=chunk.page,
                content=chunk.content,
                source_url=doc.source_url,
                tokens=tokens,
                term_freq=tf,
                length=len(tokens),
            )
        )
    return _Bm25Index(entries)


def get_index(db: Session) -> _Bm25Index:
    global _index
    if _index is None:
        with _lock:
            if _index is None:
                _index = _build(db)
    return _index


def invalidate() -> None:
    """Call after loading seed data so the next search rebuilds against the new rows."""
    global _index
    with _lock:
        _index = None


def search(db: Session, query: str, top_k: int) -> list[Hit]:
    return get_index(db).search(query, top_k)
