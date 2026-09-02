# Backend — Ask Sarthi

The chat path is live: retrieval over the seed corpus, answer generation with Gemini, and
citations that resolve back to real BIS source URLs.

## Run it

```bash
py -3.11 -m venv .venv
.venv/Scripts/pip install -r requirements-core.txt
cp .env.example .env
python -m ingestion.load_seed          # load the corpus into SQLite
cd backend && ../.venv/Scripts/python -m uvicorn app.main:app --reload
```

Frontend in a second terminal:

```bash
cd frontend && npm install && npm run dev
```

Vite proxies `/api` to `127.0.0.1:8000`, so there is no CORS hop in development.

> **Python 3.11 or 3.12, not 3.14.** `pydantic-core`, `faiss-cpu`, `easyocr` and `opencv` have
> no cp314 wheels, so pip tries to compile them from source and fails.

## The Gemini key

Get a free key at <https://aistudio.google.com/apikey>, then in `.env`:

```
GEMINI_API_KEY=<your key>
MOCK_LLM=0
```

Until you do that, `MOCK_LLM=1` keeps everything working: retrieval, citations, persistence and
the whole UI run for real, and only the wording of the answer is stubbed. That is also what CI
uses, and it is worth keeping as demo-day insurance — the demo survives a dead venue network.

`GET /api/health` reports what is actually wired:

```json
{"status":"ok","database":true,"llm_key_configured":false,"mock_llm":true}
```

The placeholder `your_key_here` counts as *not* configured, so this never reads green by accident.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| `GET`  | `/api/health` | Subsystem status |
| `POST` | `/api/chat` | Ask a question (rate limited, 20/min per IP) |
| `GET`  | `/api/chat/{session_id}/history` | Replay a conversation |
| `POST` | `/api/feedback` | Thumbs up/down on a message |

Request and response shapes are the frozen contracts in
[`backend/app/schemas/contracts.py`](../backend/app/schemas/contracts.py) — unchanged.

## How an answer is kept honest

The model supplies **wording**. It never supplies **facts**. Four gates enforce that, in order:

1. **Nothing relevant retrieved** → refuse *without calling the model at all*. This is the
   important one: it removes any opportunity for Gemini to answer about Indian law from
   parametric memory. Controlled by `RELEVANCE_THRESHOLD`.
2. **No model available** → return the retrieved source text with a warning, rather than a 500.
3. **Answer cites nothing** → force `confidence: unverified` and warn. A model-invented chunk id
   is dropped before this check, so a hallucinated citation lands here.
4. **Cited source is unverified** → cap confidence at `low` and warn.

`tests/unit/test_chat_grounding.py` pins all four. They are the tests to keep green.

```bash
.venv/Scripts/python -m pytest tests/ -q
```

## Retrieval

`app/services/retrieval.py` is BM25 in plain Python — no FAISS, no embedding model, no download.
Scores are normalised to 0–1 so `RELEVANCE_THRESHOLD` means something.

It is a deliberate placeholder. When the embedding index lands, replace `search()` with a hybrid
scorer; everything upstream depends only on its return type (`list[Hit]`). The `EMBEDDING_MODEL`,
`FAISS_INDEX_PATH` and `RERANKER_MODEL` settings are already carried in config for that.

Being lexical, it matches vocabulary rather than meaning: "bottle" will not reach a chunk that
only says "container". Adding vocabulary to a chunk's text is the cheap fix until embeddings land.

## The corpus is not verified yet

`data/seed/knowledge.json` carries a `verified` flag per document. **13 of 14 are `false`** — the
content was written from general knowledge of BIS schemes, not transcribed from the linked pages.

Wrong IS numbers in a compliance tool are worse than no answer. Before demoing: open each
`source_url`, check the text, and flip the flag. `python -m ingestion.load_seed` prints the
outstanding list every time it runs.

Standards and forms live in `standards.csv` and `forms.csv` and need the same treatment. The
form codes in particular are descriptive placeholders (`ISI-APPLY`, `CRS-APPLY`) rather than
official BIS form numbers, because BIS has largely moved to online portal submissions.

## Not built yet

`/api/scan`, `/api/match`, `/api/forms/search` and `/api/roadmap` — the contracts exist, the
routes do not. `ScanRecord`, `Standard` and `Form` tables are defined and seeded, so those
routers have somewhere to read from.

## Frontend UI notes

Typography is Jost (display, a Futura-lineage geometric) over Work Sans (body), with shared
`.eyebrow` / `.font-display` helpers in `index.css`.

Motion lives in CSS, not JS — `.animate-rise`, `.shine`, `.press`, `.link-underline`,
`.icon-tile`. There is no framer-motion; the animation work added ~2 KB to the bundle. Every
effect sits behind a `prefers-reduced-motion` block that collapses it to the final state.

`components/ui/InteractiveHoverButton.jsx` is adapted from MagicUI's Interactive Hover Button
(21st.dev), converted to JSX and re-pointed at the BIS tokens. Its colours are chosen by
`variant`, never by a caller-supplied class: `lib/cn.js` is a plain join rather than
tailwind-merge, so a passed-in `bg-*` would sit alongside the variant's own and let stylesheet
order pick the winner. Add a variant instead of overriding one.
