"""Central settings, loaded from .env. Import `settings` anywhere; never read os.environ directly."""

import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[2]

# Vercel (and most serverless runtimes) mount the deployment read-only; /tmp is the only
# writable path. Detected once here so nothing downstream has to care where it is running.
IS_SERVERLESS = bool(os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"))
WRITABLE_ROOT = Path("/tmp") if IS_SERVERLESS else ROOT


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ROOT / ".env", env_file_encoding="utf-8", extra="ignore"
    )

    # LLM
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.6-flash"
    llm_provider: str = "gemini"
    mock_llm: bool = False

    # Database
    database_url: str = "sqlite:///./bis_sarthi.db"

    # Retrieval
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    reranker_model: str = "BAAI/bge-reranker-base"
    faiss_index_path: Path = ROOT / "data" / "index"
    retrieval_top_k: int = 20
    rerank_top_n: int = 4
    relevance_threshold: float = 0.25

    # Server
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    cors_origins: str = "http://localhost:5173"
    upload_dir: Path = ROOT / "data" / "uploads"
    max_upload_mb: int = 5

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def is_serverless(self) -> bool:
        return IS_SERVERLESS

    @property
    def writable_upload_dir(self) -> Path:
        """upload_dir, redirected to /tmp on a read-only filesystem."""
        return WRITABLE_ROOT / "uploads" if IS_SERVERLESS else self.upload_dir

    @property
    def has_llm_key(self) -> bool:
        """True only for a real key.

        `.env` ships with GEMINI_API_KEY=your_key_here, and a truthiness check treats that
        placeholder as configured — which sends the app down the live path and fails with a
        confusing 400 from Google instead of the "no key" message.
        """
        key = self.gemini_api_key.strip()
        return bool(key) and key.lower() not in {"your_key_here", "changeme", "todo"}

    @property
    def resolved_database_url(self) -> str:
        """Anchor a relative SQLite path to the repo root.

        Without this, `uvicorn` (run from backend/) and `python -m ingestion.load_seed` (run
        from the repo root) each create their own bis_sarthi.db and the API sees an empty
        corpus. Non-SQLite URLs pass through untouched.
        """
        url = self.database_url
        prefix = "sqlite:///"
        if not url.startswith(prefix):
            return url
        path = url[len(prefix) :]
        if path.startswith(":memory:") or Path(path).is_absolute():
            return url
        # On serverless this lands in /tmp: writable, but wiped between cold starts. That is
        # why startup re-seeds an empty corpus. Point DATABASE_URL at Postgres for anything
        # that must actually persist, such as chat history and feedback.
        return prefix + str((WRITABLE_ROOT / path).resolve())


settings = Settings()
