"""Write your Gemini API key into .env without it passing through anything else.

    python scripts/set_key.py

Prompts for the key, writes it to .env, flips MOCK_LLM to 0, and verifies the key works by
making one real call. The key goes from your terminal straight to the file: it is never echoed,
never logged, and never printed back.

Get a key at https://aistudio.google.com/apikey
"""

from __future__ import annotations

import getpass
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV = ROOT / ".env"
EXAMPLE = ROOT / ".env.example"

PLACEHOLDERS = {"your_key_here", "changeme", "todo", ""}


def set_var(text: str, key: str, value: str) -> str:
    """Replace `key=...` in place, or append it if absent."""
    pattern = re.compile(rf"^{re.escape(key)}=.*$", re.MULTILINE)
    if pattern.search(text):
        return pattern.sub(f"{key}={value}", text)
    return text.rstrip("\n") + f"\n{key}={value}\n"


def main() -> int:
    if not ENV.exists():
        if not EXAMPLE.exists():
            print("No .env or .env.example found. Run this from the repo root.")
            return 1
        ENV.write_text(EXAMPLE.read_text(encoding="utf-8"), encoding="utf-8")
        print("Created .env from .env.example")

    print("Paste your Gemini API key (input is hidden):")
    key = getpass.getpass("  key: ").strip()

    if key.lower() in PLACEHOLDERS:
        print("That's the placeholder, not a key.")
        return 1
    if len(key) < 20:
        print("That doesn't look like an API key (too short).")
        return 1

    text = ENV.read_text(encoding="utf-8")
    text = set_var(text, "GEMINI_API_KEY", key)
    text = set_var(text, "MOCK_LLM", "0")
    ENV.write_text(text, encoding="utf-8")
    print(f"\nWrote GEMINI_API_KEY to {ENV.name} and set MOCK_LLM=0")
    print(".env is gitignored, so this will not be committed.\n")

    # Verify against the real API — a key that only *looks* right is worth nothing.
    sys.path.insert(0, str(ROOT / "backend"))
    try:
        from google import genai
    except ImportError:
        print("google-genai isn't installed; skipping the live check.")
        return 0

    model = "gemini-2.5-flash"
    for line in text.splitlines():
        if line.startswith("GEMINI_MODEL="):
            model = line.split("=", 1)[1].strip() or model

    print(f"Testing the key against {model}...")
    try:
        client = genai.Client(api_key=key)
        result = client.models.generate_content(model=model, contents="Reply with: ok")
        print(f"Success — the model replied: {(result.text or '').strip()[:40]}")
        print("\nRestart uvicorn and Ask Sarthi will use live generation.")
    except Exception as exc:
        # Deliberately truncated: provider errors sometimes echo the key back.
        print(f"The key was saved, but the test call failed: {str(exc)[:180]}")
        print("Check the key at https://aistudio.google.com/apikey")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
