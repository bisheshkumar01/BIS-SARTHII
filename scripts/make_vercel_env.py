"""Generate a paste-ready environment block for Vercel, from your existing .env.

    python scripts/make_vercel_env.py

Writes vercel-env.txt containing exactly the variables the deployed function needs. That file
is gitignored, so it cannot be committed by accident - but it holds a real key, so delete it
once you have pasted it.

Vercel > Project > Settings > Environment Variables has an import box that accepts a whole
KEY=value block at once, so the output pastes in a single step.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV = ROOT / ".env"
OUT = ROOT / "vercel-env.txt"

# Only what the function actually reads. CORS_ORIGINS is omitted on purpose: on Vercel the
# frontend and API are the same origin, so setting it would be noise. Retrieval/vision paths
# are omitted because that code does not ship to the function.
WANTED = ["GEMINI_API_KEY", "GEMINI_MODEL", "MOCK_LLM", "DATABASE_URL"]

PLACEHOLDERS = {"", "your_key_here", "changeme", "todo"}


def read_env() -> dict[str, str]:
    if not ENV.exists():
        raise SystemExit("No .env found. Run scripts/set_key.py first.")
    values: dict[str, str] = {}
    for line in ENV.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        values[k.strip()] = v.strip().strip('"').strip("'")
    return values


def main() -> int:
    env = read_env()
    lines: list[str] = []
    problems: list[str] = []

    for key in WANTED:
        value = env.get(key, "")

        if key == "GEMINI_API_KEY" and value.lower() in PLACEHOLDERS:
            problems.append("GEMINI_API_KEY is unset in .env - run scripts/set_key.py")
            continue

        if key == "MOCK_LLM":
            # Shipping MOCK_LLM=1 would deploy a demo that answers with canned text.
            if value != "0":
                problems.append(f"MOCK_LLM was {value!r} in .env; forcing 0 for production")
            value = "0"

        if key == "DATABASE_URL":
            if value.startswith("sqlite"):
                problems.append(
                    "DATABASE_URL is SQLite. On Vercel that lands in /tmp and is wiped on "
                    "every cold start, so chat history will not persist. Omitted here - set "
                    "a Postgres URL in Vercel when you want it kept."
                )
                continue
            if not value:
                continue

        lines.append(f"{key}={value}")

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {OUT.name} with {len(lines)} variables:")
    for line in lines:
        k, v = line.split("=", 1)
        shown = f"{v[:4]}...{v[-3:]} ({len(v)} chars)" if k.endswith("KEY") else v
        print(f"  {k} = {shown}")

    if problems:
        print("\nNotes:")
        for p in problems:
            print(f"  - {p}")

    print(
        "\nPaste into: Vercel > Project > Settings > Environment Variables > import."
        f"\nThen delete it:  rm {OUT.name}"
        f"\n({OUT.name} is gitignored, so it will not be committed either way.)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
