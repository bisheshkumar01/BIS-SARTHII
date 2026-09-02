"""Load data/seed/ into the database.

    python -m ingestion.load_seed          # upsert
    python -m ingestion.load_seed --reset  # drop seeded rows first

The actual loading lives in app.services.seed, because the serverless startup path needs it
too. This module is just the command-line front end.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from sqlalchemy import select  # noqa: E402

from app.db.session import Base, SessionLocal, engine  # noqa: E402
from app.models.entities import Document  # noqa: E402
from app.services.seed import load_all  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Load the BIS SARTHI seed corpus.")
    parser.add_argument("--reset", action="store_true", help="delete existing rows first")
    args = parser.parse_args()

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        print("Loading seed corpus...")
        stats = load_all(db, reset=args.reset)
        print(f"  knowledge.json  {stats['documents']} documents, {stats['chunks']} chunks")
        print(f"  standards.csv   {stats['standards']} standards")
        print(f"  forms.csv       {stats['forms']} forms")

        unverified = (
            db.execute(select(Document).where(Document.verified.is_(False))).scalars().all()
        )
        print(f"\nDone. {len(unverified)} of {stats['documents']} documents are unverified.")
        if unverified:
            print("Verify these against their source_url before demoing:")
            for d in unverified:
                print(f"  - {d.title}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
