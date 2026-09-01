"""Central settings, loaded from .env. Import `settings` anywhere; never read os.environ directly."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ROOT / ".env", env_file_encoding="utf-8", extra="ignore"
    )

    # LLM
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
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


settings = Settings()
