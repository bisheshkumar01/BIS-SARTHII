"""The ten MVP tables. Kept deliberately small — no users, labs, or fees in week one."""

from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Document(Base):
    """One ingested BIS source file or web page."""

    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(500))
    doc_type: Mapped[str] = mapped_column(String(50), default="reference")
    source_url: Mapped[str] = mapped_column(String(1000))
    # Curated seed entries are transcribed from a BIS page rather than ingested from a file,
    # so they have no content hash. Only pipeline-ingested documents carry one.
    sha256: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)
    # True once a human has checked the passage against the official source. The answer path
    # cites verified documents only, so this gates what can appear as evidence.
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    fetched_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    chunks: Mapped[list["Chunk"]] = relationship(back_populates="document")


class Chunk(Base):
    """A retrievable passage. faiss_id links it to its row in the FAISS index."""

    __tablename__ = "chunks"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"))
    content: Mapped[str] = mapped_column(Text)
    heading: Mapped[str | None] = mapped_column(String(500), nullable=True)
    section_path: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    page: Mapped[int | None] = mapped_column(Integer, nullable=True)
    chunk_index: Mapped[int | None] = mapped_column(Integer, nullable=True)
    token_count: Mapped[int] = mapped_column(Integer, default=0)
    # Set only once a vector index exists. Retrieval is BM25 on the deployed function, which
    # reads `content` directly, so seeded chunks are searchable without it.
    faiss_id: Mapped[int | None] = mapped_column(Integer, index=True, nullable=True)
    meta: Mapped[dict] = mapped_column(JSON, default=dict)

    document: Mapped[Document] = relationship(back_populates="chunks")


class Standard(Base):
    """Curated catalogue entry. Standard matching scores against this table, not against RAG."""

    __tablename__ = "standards"

    id: Mapped[int] = mapped_column(primary_key=True)
    is_number: Mapped[str] = mapped_column(String(50), index=True)  # e.g. "IS 2347:2017"
    title: Mapped[str] = mapped_column(String(500))
    scope_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str | None] = mapped_column(String(100), index=True)
    keywords: Mapped[list] = mapped_column(JSON, default=list)
    scheme: Mapped[str | None] = mapped_column(String(50))  # ISI | CRS | HALLMARK | FMCS
    is_mandatory: Mapped[bool] = mapped_column(Boolean, default=False)
    revision_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source_url: Mapped[str] = mapped_column(String(1000))


class Form(Base):
    """A real BIS form. The Form Finder may only return rows that exist here."""

    __tablename__ = "forms"

    id: Mapped[int] = mapped_column(primary_key=True)
    form_code: Mapped[str] = mapped_column(String(50), index=True)
    name: Mapped[str] = mapped_column(String(500))
    purpose: Mapped[str] = mapped_column(Text)
    scheme: Mapped[str | None] = mapped_column(String(50), index=True)
    stage: Mapped[str | None] = mapped_column(String(50), index=True)
    product_category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    official_url: Mapped[str] = mapped_column(String(1000))


class Scheme(Base):
    __tablename__ = "schemes"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(50), unique=True)
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_url: Mapped[str] = mapped_column(String(1000))


class ChatSession(Base):
    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    language: Mapped[str] = mapped_column(String(10), default="en")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)


class ChatMessage(Base):
    """One turn of a conversation.

    citations_json holds the evidence for an assistant turn, serialised from the Citation
    schema. Keeping it on the row means an answer and the sources it was built from are
    written in a single insert, which matters on serverless where /tmp is wiped between
    cold starts and a half-written answer would outlive its evidence.
    """

    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.id"), index=True)
    role: Mapped[str] = mapped_column(String(20))  # user | assistant
    content: Mapped[str] = mapped_column(Text)
    intent: Mapped[str | None] = mapped_column(String(50), nullable=True)
    confidence: Mapped[str | None] = mapped_column(String(20), nullable=True)
    citations_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    citations: Mapped[list["Citation"]] = relationship(back_populates="message")


class Citation(Base):
    """Ties an answer back to the exact chunk that supports it."""

    __tablename__ = "citations"

    id: Mapped[int] = mapped_column(primary_key=True)
    message_id: Mapped[int] = mapped_column(ForeignKey("messages.id"), index=True)
    chunk_id: Mapped[int] = mapped_column(ForeignKey("chunks.id"))
    snippet: Mapped[str] = mapped_column(Text)
    rank: Mapped[int] = mapped_column(Integer, default=0)
    score: Mapped[float] = mapped_column(Float, default=0.0)

    message: Mapped[ChatMessage] = relationship(back_populates="citations")


class Scan(Base):
    """A product image upload: what we extracted, and what the user corrected it to."""

    __tablename__ = "scans"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)
    image_path: Mapped[str] = mapped_column(String(1000))
    extracted: Mapped[dict] = mapped_column(JSON, default=dict)
    confirmed: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)


class Roadmap(Base):
    __tablename__ = "roadmaps"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[str] = mapped_column(String(64), index=True)
    product: Mapped[dict] = mapped_column(JSON, default=dict)
    scheme: Mapped[str | None] = mapped_column(String(50), nullable=True)
    steps: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)


class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(primary_key=True)
    message_id: Mapped[int | None] = mapped_column(ForeignKey("messages.id"), nullable=True)
    is_helpful: Mapped[bool] = mapped_column(Boolean)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)
