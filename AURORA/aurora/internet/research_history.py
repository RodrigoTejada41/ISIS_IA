from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path


class ResearchHistory:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS research_history (
                    id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    query TEXT NOT NULL,
                    mode TEXT NOT NULL,
                    status TEXT NOT NULL,
                    sources TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    metadata TEXT NOT NULL
                )
                """
            )

    def add(self, research_id: str, query: str, mode: str, status: str, sources: list[dict], summary: str, metadata: dict | None = None) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO research_history VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    research_id,
                    time.strftime("%Y-%m-%dT%H:%M:%S"),
                    query,
                    mode,
                    status,
                    json.dumps(sources, ensure_ascii=False),
                    summary,
                    json.dumps(metadata or {}, ensure_ascii=False),
                ),
            )

    def list(self, limit: int = 20) -> list[dict]:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("SELECT id, created_at, query, mode, status, sources, summary, metadata FROM research_history ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
        return [
            {"id": row[0], "created_at": row[1], "query": row[2], "mode": row[3], "status": row[4], "sources": json.loads(row[5]), "summary": row[6], "metadata": json.loads(row[7])}
            for row in rows
        ]
