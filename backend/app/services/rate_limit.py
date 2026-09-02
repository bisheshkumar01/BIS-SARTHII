"""Shared rate limiter.

Gemini free-tier quota is the scarce resource here — one open tab hammering /api/chat can
exhaust the day's requests. Keyed by client IP, in-memory: fine for a single-process MVP,
swap the storage backend for Redis if this ever runs multi-worker.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
