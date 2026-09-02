# Deploying to Vercel

One Vercel project serves both halves: the Vite build as static files, and the FastAPI app as a
Python serverless function at `/api/*`. Config is [`vercel.json`](../vercel.json) at the repo root.

```
vercel.json          buildCommand → frontend/dist, functions → api/index.py
api/index.py         re-exports backend/app/main.py:app for the Python runtime
api/requirements.txt the function's dependencies (NOT the root requirements.txt)
```

## Environment variables to set in Vercel

Project → Settings → Environment Variables:

| Variable | Value | Why |
|---|---|---|
| `GEMINI_API_KEY` | your key | Without it the API returns raw source text instead of written answers |
| `MOCK_LLM` | `0` | `1` replays canned responses |
| `DATABASE_URL` | a Postgres URL | **See the persistence note below** |
| `GEMINI_MODEL` | `gemini-3.6-flash` | Optional; this is the default |

`CORS_ORIGINS` is not needed — the frontend and API are same-origin on Vercel.

## Locally

Never commit a key. `.env` is gitignored; set it with:

```bash
python scripts/set_key.py
```

It prompts (hidden input), writes `.env`, sets `MOCK_LLM=0`, and makes one live call to confirm
the key actually works.

## Three things that bite on serverless

**1. The filesystem is read-only except `/tmp`.** `config.py` detects Vercel and redirects the
SQLite file and upload dir there. Startup tolerates a failed `mkdir` rather than crash-looping.

**2. `/tmp` is wiped between cold starts.** So a fresh instance boots with an empty database.
`ensure_seeded()` in `app/services/seed.py` reloads `data/seed/` when the corpus is empty,
which keeps a cold instance answering instead of refusing everything.

The corollary: **on SQLite, chat history and feedback do not survive a cold start.** Point
`DATABASE_URL` at Postgres (Supabase's free tier is fine) for anything that must persist:

```
DATABASE_URL=postgresql+pg8000://postgres:<password>@<host>:5432/postgres
```

`pg8000` is in `api/requirements.txt` because it is pure Python — `psycopg2` needs a build step
the runtime does not have.

**3. Rate limiting is per-instance.** `slowapi` stores counters in memory, so the 20/min limit
applies per warm instance rather than globally. Move it to Redis if that matters.

## Why the function has its own requirements.txt

Vercel caps an unzipped function at 250 MB. The root `requirements.txt` pulls `faiss-cpu`,
`sentence-transformers` (and torch behind it), `easyocr` and `opencv` — comfortably past that.
`api/requirements.txt` therefore carries the chat path only.

This is also why retrieval is BM25 in pure Python: nothing to ship. Moving to embeddings means
moving retrieval *off* the function — a hosted vector DB — rather than fattening that file.

## GitHub Pages

`.github/workflows/deploy.yml` is now **manual-only**. It publishes the frontend alone, so when
it ran on every push it shipped a build whose `/api` calls 404'd, racing the Vercel deploy. Run
it from the Actions tab only as a fallback.

## Verifying a deploy

```bash
curl https://<your-app>.vercel.app/api/health
```

Expect `llm_key_configured: true` and `mock_llm: false`. If you get HTML instead of JSON, the
function did not build — check the Vercel build log for `api/index.py`.
