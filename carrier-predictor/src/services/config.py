"""Configuration management."""

import os
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    # Embedding Model
    embed_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"

    # Data Directories
    index_dir: str = "data/index"
    docs_dir: str = "data/carriers"

    # Optional OpenAI
    openai_api_key: Optional[str] = None
    enable_openai_scoring: bool = False

    # Logging
    log_level: str = "INFO"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Config files
    carriers_yaml_path: str = "src/config/carriers.yaml"
    portal_links_json_path: str = "src/config/portal_links.json"

    # Retrieval settings
    top_k: int = 10
    chunk_size: int = 800
    chunk_overlap: int = 100

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    def ensure_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        Path(self.index_dir).mkdir(parents=True, exist_ok=True)
        Path(self.docs_dir).mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
settings.ensure_directories()
