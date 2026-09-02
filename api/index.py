"""Vercel serverless entrypoint.

Vercel's Python runtime looks for a module-level ASGI/WSGI `app`. Everything real lives in
backend/app; this file only puts that package on the path and re-exports it, so the same
application runs locally under uvicorn and in production as a function.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.main import app  # noqa: E402,F401  — re-exported for the runtime to discover
