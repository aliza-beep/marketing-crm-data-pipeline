from __future__ import annotations

import re
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from .config import Settings

SQLITE_SCHEMA = """
CREATE TABLE IF NOT EXISTS pipeline_runs (
  run_id TEXT PRIMARY KEY, started_at TEXT NOT NULL, completed_at TEXT,
  status TEXT NOT NULL, rows_extracted INTEGER DEFAULT 0,
  rows_loaded INTEGER DEFAULT 0, error_message TEXT
);
CREATE TABLE IF NOT EXISTS ad_performance (
  event_date TEXT NOT NULL, source TEXT NOT NULL, campaign_id TEXT NOT NULL,
  campaign_name TEXT NOT NULL, impressions INTEGER NOT NULL CHECK(impressions >= 0),
  clicks INTEGER NOT NULL CHECK(clicks >= 0), spend REAL NOT NULL CHECK(spend >= 0),
  platform_conversions INTEGER NOT NULL CHECK(platform_conversions >= 0),
  currency TEXT NOT NULL, is_simulated INTEGER NOT NULL,
  loaded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY(event_date, source, campaign_id)
);
CREATE TABLE IF NOT EXISTS web_analytics (
  event_date TEXT NOT NULL, source TEXT NOT NULL, campaign_id TEXT NOT NULL,
  sessions INTEGER NOT NULL CHECK(sessions >= 0),
  engaged_sessions INTEGER NOT NULL CHECK(engaged_sessions >= 0),
  is_simulated INTEGER NOT NULL, loaded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY(event_date, source, campaign_id)
);
CREATE TABLE IF NOT EXISTS crm_leads (
  lead_id TEXT PRIMARY KEY, created_date TEXT NOT NULL, source TEXT NOT NULL,
  campaign_id TEXT NOT NULL, lead_score INTEGER NOT NULL CHECK(lead_score BETWEEN 0 AND 100),
  status TEXT NOT NULL, revenue REAL NOT NULL CHECK(revenue >= 0),
  is_simulated INTEGER NOT NULL, loaded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS webhook_events (
  event_id TEXT PRIMARY KEY, received_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  event_type TEXT NOT NULL, payload_json TEXT NOT NULL, processed INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS data_quality_results (
  id INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT NOT NULL, checked_at TEXT NOT NULL,
  check_name TEXT NOT NULL, status TEXT NOT NULL, details TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS anomalies (
  id INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT NOT NULL, event_date TEXT NOT NULL,
  source TEXT NOT NULL, metric TEXT NOT NULL, observed_value REAL NOT NULL,
  baseline_value REAL NOT NULL, severity TEXT NOT NULL, description TEXT NOT NULL
);
"""


def sqlite_path(url: str) -> Path:
    match = re.fullmatch(r"sqlite:///([^?]+)", url)
    if not match:
        raise ValueError("SQLite URL must use sqlite:///relative/path.db")
    return Path(match.group(1))


class Database:
    def __init__(self, settings: Settings):
        self.settings = settings

    @contextmanager
    def connect(self) -> Iterator[Any]:
        if self.settings.is_postgres:
            import psycopg
            conn = psycopg.connect(self.settings.database_url)
        else:
            path = sqlite_path(self.settings.database_url)
            path.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(path)
            conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def initialize(self) -> None:
        with self.connect() as conn:
            if self.settings.is_postgres:
                schema = Path("sql/schema_postgres.sql").read_text(encoding="utf-8")
                with conn.cursor() as cur:
                    cur.execute(schema)
            else:
                conn.executescript(SQLITE_SCHEMA)

    @property
    def placeholder(self) -> str:
        return "%s" if self.settings.is_postgres else "?"

    def execute(self, sql: str, params: tuple = ()) -> None:
        with self.connect() as conn:
            conn.execute(sql, params)

    def query(self, sql: str, params: tuple = ()) -> list[dict[str, Any]]:
        with self.connect() as conn:
            cursor = conn.execute(sql, params)
            columns = [item[0] for item in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def upsert_many(self, table: str, rows: list[dict[str, Any]], keys: list[str]) -> int:
        if not rows:
            return 0
        allowed = {"ad_performance", "web_analytics", "crm_leads"}
        if table not in allowed:
            raise ValueError(f"Unsafe table: {table}")
        columns = list(rows[0])
        placeholders = ",".join([self.placeholder] * len(columns))
        updates = [c for c in columns if c not in keys]
        sql = (f"INSERT INTO {table} ({','.join(columns)}) VALUES ({placeholders}) "
               f"ON CONFLICT ({','.join(keys)}) DO UPDATE SET " +
               ",".join(f"{c}=excluded.{c}" for c in updates))
        values = [tuple(row[c] for c in columns) for row in rows]
        with self.connect() as conn:
            conn.executemany(sql, values)
        return len(rows)

