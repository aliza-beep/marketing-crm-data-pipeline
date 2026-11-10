from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - supports dependency-light diagnostics
    load_dotenv = lambda: None

load_dotenv()


@dataclass(frozen=True)
class Settings:
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///data/marketing.db")
    app_env: str = os.getenv("APP_ENV", "development")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    simulation_seed: int = int(os.getenv("SIMULATION_SEED", "42"))
    webhook_secret: str = os.getenv("WEBHOOK_SECRET", "development-only-secret")
    log_path: Path = Path(os.getenv("PIPELINE_LOG_PATH", "logs/pipeline.jsonl"))

    @property
    def is_postgres(self) -> bool:
        return self.database_url.startswith(("postgresql://", "postgres://"))


settings = Settings()

