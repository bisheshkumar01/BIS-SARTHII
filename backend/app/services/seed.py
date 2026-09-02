"""Load data/seed/ into the database.

Lives in the app (not in ingestion/) because serverless needs it too: on Vercel the filesystem
is ephemeral, so a cold start can come up against an empty database. `ensure_seeded()` runs at
startup and fills it, which makes a fresh instance self-healing instead of answering every
question with "no source found".

Idempotent: documents key on source_url + title, chunks on their heading within a document.
"""

from __future__ import annotations

import csv
import json
import logging
from pathlib import Path

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.models.entities import Chunk, Document, Form, Standard

log = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[3]
SEED_DIR = ROOT / "data" / "seed"


def load_knowledge(db: Session, reset: bool = False) -> tuple[int, int]:
    path = SEED_DIR / "knowledge.json"
    if not path.exists():
        log.warning("%s not found — skipping", path)
        return 0, 0

    if reset:
        db.execute(delete(Chunk))
        db.execute(delete(Document))
        db.flush()

    docs = json.loads(path.read_text(encoding="utf-8"))
    n_docs = n_chunks = 0

    for entry in docs:
        doc = db.execute(
            select(Document).where(
                Document.source_url == entry["source_url"], Document.title == entry["title"]
            )
        ).scalar_one_or_none()

        if doc is None:
            doc = Document(title=entry["title"], source_url=entry["source_url"])
            db.add(doc)
        doc.doc_type = entry.get("doc_type", "reference")
        doc.verified = bool(entry.get("verified", False))
        db.flush()
        n_docs += 1

        existing = {c.heading: c for c in doc.chunks}
        seen: set[str | None] = set()
        for c in entry["chunks"]:
            heading = c.get("heading")
            seen.add(heading)
            row = existing.get(heading)
            if row is None:
                row = Chunk(document_id=doc.id, heading=heading)
                db.add(row)
            row.content = c["content"]
            row.page = c.get("page")
            n_chunks += 1

        # Drop chunks removed from the JSON, so deletions propagate.
        for heading, row in existing.items():
            if heading not in seen:
                db.delete(row)

    return n_docs, n_chunks


def load_csv(db: Session, filename: str, model, key_field: str, fields: list[str]) -> int:
    path = SEED_DIR / filename
    if not path.exists():
        log.warning("%s not found — skipping", path)
        return 0

    count = 0
    with path.open(encoding="utf-8", newline="") as fh:
        for raw in csv.DictReader(fh):
            row = {f: (raw.get(f) or "").strip() for f in fields}
            key = row[key_field]
            if not key:
                continue
            obj = db.execute(
                select(model).where(getattr(model, key_field) == key)
            ).scalar_one_or_none()
            if obj is None:
                obj = model()
                db.add(obj)
            for field, value in row.items():
                if field == "is_mandatory":
                    value = value.lower() in ("1", "true", "yes", "y")
                setattr(obj, field, value)
            count += 1
    return count


def load_all(db: Session, reset: bool = False) -> dict[str, int]:
    """Load every seed file. Commits before returning."""
    n_docs, n_chunks = load_knowledge(db, reset)
    n_std = load_csv(
        db,
        "standards.csv",
        Standard,
        "is_number",
        ["is_number", "title", "scope", "keywords", "scheme", "is_mandatory", "source_url"],
    )
    n_forms = load_csv(
        db,
        "forms.csv",
        Form,
        "form_code",
        ["form_code", "name", "purpose", "scheme", "stage", "official_url"],
    )
    db.commit()

    from app.services import retrieval

    retrieval.invalidate()
    return {
        "documents": n_docs,
        "chunks": n_chunks,
        "standards": n_std,
        "forms": n_forms,
    }


def ensure_seeded(db: Session) -> bool:
    """Seed only if the corpus is empty. Safe to call on every cold start.

    Returns True if it actually loaded anything. A failure here is logged, never raised: an
    unseeded instance still serves health checks and refuses questions honestly, which beats
    a boot loop.
    """
    try:
        if db.execute(select(func.count()).select_from(Document)).scalar_one():
            return False
        log.info("Corpus empty — loading seed data")
        stats = load_all(db)
        log.info("Seeded %s", stats)
        return True
    except Exception:
        log.exception("Could not seed the corpus; continuing with an empty index")
        db.rollback()
        return False
