from __future__ import annotations

import sqlite3
import time
import uuid
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from .audit import AuditEvent, AuditLogger


class MemoryType(str, Enum):
    SESSION = "SESSION"
    CONVERSATION = "CONVERSATION"
    PREFERENCE = "PREFERENCE"
    CONFIRMED_FACT = "CONFIRMED_FACT"
    PROJECT_KNOWLEDGE = "PROJECT_KNOWLEDGE"
    PROCEDURE = "PROCEDURE"
    SKILL = "SKILL"
    ERROR_SOLUTION = "ERROR_SOLUTION"
    TEMPORARY = "TEMPORARY"
    SENSITIVE = "SENSITIVE"


class MemoryStatus(str, Enum):
    PROPOSED = "PROPOSED"
    CONFIRMED = "CONFIRMED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    ARCHIVED = "ARCHIVED"


@dataclass(frozen=True, slots=True)
class MemoryRecord:
    content: str
    type: MemoryType
    origin: str
    user: str
    confidence: float = 1.0
    sensitivity: str = "LOW"
    project: str | None = None
    tags: str = ""
    status: MemoryStatus = MemoryStatus.PROPOSED
    expires_at: float | None = None
    id: str = ""


class MemoryStore:
    def __init__(self, db_path: str | Path, audit: AuditLogger) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.audit = audit
        self._init()

    def _init(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS memory_records (
                  id TEXT PRIMARY KEY, type TEXT, content TEXT, origin TEXT,
                  created_at REAL, updated_at REAL, confidence REAL,
                  sensitivity TEXT, expires_at REAL, tags TEXT, project TEXT,
                  user TEXT, status TEXT
                )
                """
            )

    def add(self, record: MemoryRecord) -> str:
        record_id = record.id or str(uuid.uuid4())
        now = time.time()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO memory_records VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    record_id,
                    record.type.value,
                    record.content,
                    record.origin,
                    now,
                    now,
                    record.confidence,
                    record.sensitivity,
                    record.expires_at,
                    record.tags,
                    record.project,
                    record.user,
                    record.status.value,
                ),
            )
        self.audit.record(AuditEvent(action="memory.add", component="memory", params={"id": record_id, "type": record.type.value}))
        return record_id

    def set_status(self, record_id: str, status: MemoryStatus) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("UPDATE memory_records SET status = ?, updated_at = ? WHERE id = ?", (status.value, time.time(), record_id))
        self.audit.record(AuditEvent(action="memory.status", component="memory", params={"id": record_id, "status": status.value}))

    def list_by_status(self, status: MemoryStatus | None = None, limit: int = 20, include_sensitive: bool = False) -> list[dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            if status:
                rows = conn.execute(
                    """
                    SELECT * FROM memory_records
                    WHERE status = ? AND (? OR sensitivity != 'HIGH')
                    ORDER BY updated_at DESC
                    LIMIT ?
                    """,
                    (status.value, include_sensitive, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT * FROM memory_records
                    WHERE (? OR sensitivity != 'HIGH')
                    ORDER BY updated_at DESC
                    LIMIT ?
                    """,
                    (include_sensitive, limit),
                ).fetchall()
        result = [dict(row) for row in rows]
        self.audit.record(AuditEvent(action="memory.list_by_status", component="memory", params={"status": status.value if status else None, "count": len(result)}))
        return result

    def search_text(self, query: str, limit: int = 5, include_sensitive: bool = False) -> list[dict]:
        now = time.time()
        pattern = f"%{query}%"
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """
                SELECT * FROM memory_records
                WHERE content LIKE ?
                  AND status = ?
                  AND (expires_at IS NULL OR expires_at > ?)
                  AND (? OR sensitivity != 'HIGH')
                ORDER BY updated_at DESC
                LIMIT ?
                """,
                (pattern, MemoryStatus.CONFIRMED.value, now, include_sensitive, limit),
            ).fetchall()
        result = [dict(row) for row in rows]
        self.audit.record(AuditEvent(action="memory.search_text", component="memory", params={"query": query, "count": len(result)}))
        return result


class EmbeddingProvider:
    def embed(self, text: str) -> list[float]:
        tokens = text.lower().split()
        return [float(len(tokens)), float(sum(len(t) for t in tokens))]


class RagService:
    def __init__(self, store: MemoryStore, audit: AuditLogger, max_documents: int = 5, max_context_chars: int = 4000) -> None:
        self.store = store
        self.audit = audit
        self.max_documents = max_documents
        self.max_context_chars = max_context_chars

    def build_context(self, question: str, include_sensitive: bool = False) -> tuple[str, list[str]]:
        rows = self.store.search_text(question, self.max_documents, include_sensitive)
        chunks: list[str] = []
        ids: list[str] = []
        used = 0
        for row in rows:
            content = f"[{row['id']}] {row['content']}"
            if used + len(content) > self.max_context_chars:
                break
            chunks.append(content)
            ids.append(row["id"])
            used += len(content)
        self.audit.record(AuditEvent(action="rag.context", component="memory", params={"question": question, "memory_ids": ids}))
        return "\n".join(chunks), ids
