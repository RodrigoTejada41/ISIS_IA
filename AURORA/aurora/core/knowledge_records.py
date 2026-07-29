from __future__ import annotations

import sqlite3
import time
import uuid
from dataclasses import dataclass
from pathlib import Path

from aurora.core.audit import AuditEvent, AuditLogger


@dataclass(frozen=True, slots=True)
class DecisionRecord:
    project: str
    description: str
    context: str
    source_path: str
    version: str = "1"
    status: str = "ACTIVE"
    id: str = ""


@dataclass(frozen=True, slots=True)
class BugRecord:
    project: str
    title: str
    description: str
    source_path: str
    status: str = "OPEN"
    priority: str = "NORMAL"
    version: str = "1"
    id: str = ""


class KnowledgeRecordStore:
    def __init__(self, db_path: str | Path, audit: AuditLogger) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.audit = audit
        self._init()

    def _init(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS decisions (
                    id TEXT PRIMARY KEY, project TEXT, description TEXT, context TEXT,
                    source_path TEXT, version TEXT, status TEXT, created_at REAL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS bugs (
                    id TEXT PRIMARY KEY, project TEXT, title TEXT, description TEXT,
                    source_path TEXT, status TEXT, priority TEXT, version TEXT, created_at REAL
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_decisions_project ON decisions(project)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_bugs_project ON bugs(project)")

    def add_decision(self, record: DecisionRecord) -> str:
        record_id = record.id or str(uuid.uuid4())
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO decisions VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (record_id, record.project, record.description, record.context, record.source_path, record.version, record.status, time.time()),
            )
        self.audit.record(AuditEvent(action="knowledge.decision.add", component="knowledge", params={"id": record_id, "project": record.project}))
        return record_id

    def add_bug(self, record: BugRecord) -> str:
        record_id = record.id or str(uuid.uuid4())
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO bugs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (record_id, record.project, record.title, record.description, record.source_path, record.status, record.priority, record.version, time.time()),
            )
        self.audit.record(AuditEvent(action="knowledge.bug.add", component="knowledge", params={"id": record_id, "project": record.project}))
        return record_id

    def import_from_project_memory(self, project_memory_db: str | Path, limit: int | None = None) -> dict:
        sql = "SELECT path,title,project,category FROM indexed_notes WHERE category IN ('DECISION','BUG') ORDER BY modified_at DESC"
        if limit:
            sql += f" LIMIT {int(limit)}"
        decisions = bugs = 0
        with sqlite3.connect(project_memory_db) as source, sqlite3.connect(self.db_path) as dest:
            source.row_factory = sqlite3.Row
            for row in source.execute(sql):
                stable_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"{row['category']}:{row['path']}"))
                if row["category"] == "DECISION":
                    dest.execute(
                        "INSERT OR REPLACE INTO decisions VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                        (stable_id, row["project"], row["title"], "Imported from project memory", row["path"], "1", "ACTIVE", time.time()),
                    )
                    decisions += 1
                else:
                    dest.execute(
                        "INSERT OR REPLACE INTO bugs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (stable_id, row["project"], row["title"], "Imported from project memory", row["path"], "OPEN", "NORMAL", "1", time.time()),
                    )
                    bugs += 1
        result = {"decisions": decisions, "bugs": bugs}
        self.audit.record(AuditEvent(action="knowledge.import", component="knowledge", params=result))
        return result

    def search_decisions(self, query: str, limit: int = 20) -> list[dict]:
        return self._search("decisions", ["project", "description", "context", "source_path"], query, limit)

    def search_bugs(self, query: str, limit: int = 20) -> list[dict]:
        return self._search("bugs", ["project", "title", "description", "source_path"], query, limit)

    def stats(self) -> dict:
        with sqlite3.connect(self.db_path) as conn:
            decisions = conn.execute("SELECT COUNT(*) FROM decisions").fetchone()[0]
            bugs = conn.execute("SELECT COUNT(*) FROM bugs").fetchone()[0]
        return {"decisions": decisions, "bugs": bugs}

    def _search(self, table: str, fields: list[str], query: str, limit: int) -> list[dict]:
        where = " OR ".join(f"{field} LIKE ?" for field in fields)
        params = [f"%{query}%" for _ in fields] + [limit]
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(f"SELECT * FROM {table} WHERE {where} LIMIT ?", params).fetchall()
        return [dict(row) for row in rows]
