"""Gemini client.

Two things matter here:
  * `MOCK_LLM=1` returns canned JSON with no network call, so the demo survives a dead venue
    Wi-Fi and CI never needs a key.
  * Every call goes through `generate_json`, which enforces a response schema. The chat
    service depends on getting parseable JSON; free-form prose would break the contract.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from app.config import settings

log = logging.getLogger(__name__)


class LLMError(RuntimeError):
    """Raised when the model is unreachable or returns something unparseable."""


class LLMUnavailable(LLMError):
    """No API key configured and mock mode is off."""


_client = None


def _get_client():
    global _client
    if _client is None:
        from google import genai  # imported lazily so mock mode needs no SDK at import time

        if not settings.has_llm_key:
            raise LLMUnavailable(
                "GEMINI_API_KEY is not set. Add it to .env, or set MOCK_LLM=1 to run offline."
            )
        _client = genai.Client(api_key=settings.gemini_api_key)
    return _client


def is_available() -> bool:
    return settings.mock_llm or settings.has_llm_key


def _strip_fence(text: str) -> str:
    """Gemini honours response_mime_type, but a fenced block still shows up occasionally."""
    t = text.strip()
    if t.startswith("```"):
        t = t.split("\n", 1)[-1] if "\n" in t else t
        t = t.rsplit("```", 1)[0]
    return t.strip()


def generate_json(
    *,
    system_instruction: str,
    prompt: str,
    schema: dict[str, Any],
    mock_response: dict[str, Any],
    temperature: float = 0.2,
) -> dict[str, Any]:
    """Return a JSON object from the model, or `mock_response` when mocking.

    `schema` is an OpenAPI-style dict passed to Gemini as `response_schema`. Structured output
    is what lets the caller trust the keys exist.
    """
    if settings.mock_llm:
        log.info("MOCK_LLM=1 — returning canned response")
        return mock_response

    from google.genai import types

    client = _get_client()
    try:
        result = client.models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=temperature,
                response_mime_type="application/json",
                response_schema=schema,
                # The assistant must refuse rather than improvise, so give it room to
                # reproduce source wording, but not enough to ramble.
                max_output_tokens=1600,
            ),
        )
    except Exception as exc:  # SDK raises a wide range of transport/auth errors
        log.exception("Gemini call failed")
        raise LLMError(str(exc)) from exc

    text = (result.text or "").strip()
    if not text:
        raise LLMError("Gemini returned an empty response")

    try:
        parsed = json.loads(_strip_fence(text))
    except json.JSONDecodeError as exc:
        log.error("Gemini returned non-JSON: %s", text[:500])
        raise LLMError("Model response was not valid JSON") from exc

    if not isinstance(parsed, dict):
        raise LLMError("Model response was not a JSON object")
    return parsed
