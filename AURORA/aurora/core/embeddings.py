from __future__ import annotations

import json
import hashlib
import math
import sqlite3
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from aurora.core.audit import AuditEvent, AuditLogger
from aurora.core.memory import MemoryStatus


@dataclass(frozen=True, slots=True)
class EmbeddingResult:
    id: str
    content: str
    score: float
    source: str


class OllamaEmbeddingProvider:
    def __init__(self, model: str = "nomic-embed-text:latest", base_url: str = "http://127.0.0.1:11434", timeout_seconds: int = 120) -> None:
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def embed(self, text: str) -> list[float]:
        try:
            return self._embed_current(text)
        except (OSError, urllib.error.URLError, KeyError, ValueError):
            return self._embed_legacy(text)

    def _embed_current(self, text: str) -> list[float]:
        payload = {"model": self.model, "input": text}
        data = self._post("/api/embed", payload)
        vectors = data.get("embeddings") or []
        if vectors and isinstance(vectors[0], list):
            return [float(value) for value in vectors[0]]
        raise ValueError("empty embedding")

    def _embed_legacy(self, text: str) -> list[float]:
        payload = {"model": self.model, "prompt": text}
        data = self._post("/api/embeddings", payload)
        vector = data.get("embedding") or []
        if not vector:
            raise ValueError("empty embedding")
        return [float(value) for value in vector]

    def _post(self, path: str, payload: dict) -> dict:
        req = urllib.request.Request(
            f"{self.base_url}{path}",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=self.timeout_seconds) as response:
            return json.loads(response.read().decode("utf-8"))


class MemoryEmbeddingIndex:
    def __init__(self, memory_db: str | Path, embedding_db: str | Path, audit: AuditLogger, provider: OllamaEmbeddingProvider | None = None) -> None:
        self.memory_db = Path(memory_db)
        self.embedding_db = Path(embedding_db)
        self.embedding_db.parent.mkdir(parents=True, exist_ok=True)
        self.audit = audit
        self.provider = provider or OllamaEmbeddingProvider()
        self._init()

    def _init(self) -> None:
        with sqlite3.connect(self.embedding_db) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS memory_embeddings (
                  memory_id TEXT PRIMARY KEY,
                  model TEXT NOT NULL,
                  vector_json TEXT NOT NULL,
                  content_hash TEXT NOT NULL,
                  updated_at REAL NOT NULL
                )
                """
            )

    def index_confirmed(self, limit: int = 100) -> dict:
        started = time.time()
        rows = self._confirmed_rows(limit)
        indexed = 0
        skipped = 0
        with sqlite3.connect(self.embedding_db) as conn:
            for row in rows:
                content_hash = hashlib.sha256(row["content"].encode("utf-8")).hexdigest()
                current = conn.execute("SELECT content_hash, model FROM memory_embeddings WHERE memory_id = ?", (row["id"],)).fetchone()
                if current and current[0] == content_hash and current[1] == self.provider.model:
                    skipped += 1
                    continue
                vector = self.provider.embed(row["content"])
                conn.execute(
                    "INSERT OR REPLACE INTO memory_embeddings VALUES (?, ?, ?, ?, ?)",
                    (row["id"], self.provider.model, json.dumps(vector), content_hash, time.time()),
                )
                indexed += 1
        result = {"indexed": indexed, "skipped": skipped, "seen": len(rows), "model": self.provider.model}
        self.audit.record(AuditEvent(action="memory_embeddings.index", component="memory", params=result, duration_ms=int((time.time() - started) * 1000)))
        return result

    def search(self, query: str, limit: int = 5) -> list[EmbeddingResult]:
        started = time.time()
        rows = self._embedding_rows()
        if not rows:
            self.audit.record(AuditEvent(action="memory_embeddings.search", component="memory", params={"query": query, "count": 0}, duration_ms=int((time.time() - started) * 1000)))
            return []
        query_vector = self.provider.embed(query)
        memory = {row["id"]: row for row in self._confirmed_rows(10000)}
        results: list[EmbeddingResult] = []
        for row in rows:
            record = memory.get(row["memory_id"])
            if not record:
                continue
            score = _cosine(query_vector, json.loads(row["vector_json"]))
            results.append(EmbeddingResult(row["memory_id"], record["content"], score, "memory_embeddings"))
        ordered = sorted(results, key=lambda item: item.score, reverse=True)[:limit]
        self.audit.record(AuditEvent(action="memory_embeddings.search", component="memory", params={"query": query, "count": len(ordered)}, duration_ms=int((time.time() - started) * 1000)))
        return ordered

    def _confirmed_rows(self, limit: int) -> list[sqlite3.Row]:
        if not self.memory_db.exists():
            return []
        with sqlite3.connect(self.memory_db) as conn:
            conn.row_factory = sqlite3.Row
            return conn.execute(
                """
                SELECT id, content FROM memory_records
                WHERE status = ? AND sensitivity != 'HIGH'
                ORDER BY updated_at DESC
                LIMIT ?
                """,
                (MemoryStatus.CONFIRMED.value, limit),
            ).fetchall()

    def _embedding_rows(self) -> list[sqlite3.Row]:
        with sqlite3.connect(self.embedding_db) as conn:
            conn.row_factory = sqlite3.Row
            return conn.execute("SELECT memory_id, vector_json FROM memory_embeddings WHERE model = ?", (self.provider.model,)).fetchall()


def _cosine(left: list[float], right: list[float]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0
    dot = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(a * a for a in left))
    right_norm = math.sqrt(sum(b * b for b in right))
    if not left_norm or not right_norm:
        return 0.0
    return dot / (left_norm * right_norm)


@dataclass(frozen=True, slots=True)
class ProjectEmbeddingResult:
    path: str
    title: str
    project: str
    category: str
    score: float
    source: str


class ProjectEmbeddingIndex:
    def __init__(self, project_db: str | Path, embedding_db: str | Path, audit: AuditLogger, provider: OllamaEmbeddingProvider | None = None) -> None:
        self.project_db = Path(project_db)
        self.embedding_db = Path(embedding_db)
        self.embedding_db.parent.mkdir(parents=True, exist_ok=True)
        self.audit = audit
        self.provider = provider or OllamaEmbeddingProvider()
        self._init()

    def _init(self) -> None:
        with sqlite3.connect(self.embedding_db) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS project_note_embeddings (
                  path TEXT PRIMARY KEY,
                  model TEXT NOT NULL,
                  vector_json TEXT NOT NULL,
                  content_hash TEXT NOT NULL,
                  title TEXT NOT NULL,
                  project TEXT NOT NULL,
                  category TEXT NOT NULL,
                  updated_at REAL NOT NULL
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_project_note_embeddings_project ON project_note_embeddings(project)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_project_note_embeddings_category ON project_note_embeddings(category)")

    def index_notes(self, limit: int = 50, project: str | None = None, category: str | None = None, max_chars: int = 4000) -> dict:
        started = time.time()
        rows = self._candidate_rows(limit, project, category)
        indexed = 0
        skipped = 0
        missing = 0
        with sqlite3.connect(self.embedding_db) as conn:
            for row in rows:
                current = conn.execute("SELECT content_hash, model FROM project_note_embeddings WHERE path = ?", (row["path"],)).fetchone()
                if current and current[0] == row["content_hash"] and current[1] == self.provider.model:
                    skipped += 1
                    continue
                path = Path(row["path"])
                if not path.exists() or not path.is_file():
                    missing += 1
                    continue
                text = path.read_text(encoding="utf-8", errors="ignore")[:max_chars]
                payload = f"{row['title']}\nProjeto: {row['project']}\nCategoria: {row['category']}\nTags: {row['tags']}\n\n{text}".strip()
                vector = self.provider.embed(payload)
                conn.execute(
                    "INSERT OR REPLACE INTO project_note_embeddings VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (row["path"], self.provider.model, json.dumps(vector), row["content_hash"], row["title"], row["project"], row["category"], time.time()),
                )
                indexed += 1
        result = {"indexed": indexed, "skipped": skipped, "missing": missing, "seen": len(rows), "model": self.provider.model}
        self.audit.record(AuditEvent(action="project_embeddings.index", component="memory", params=result, duration_ms=int((time.time() - started) * 1000)))
        return result

    def index_batches(self, batch_size: int = 50, max_batches: int = 1, project: str | None = None, category: str | None = None, max_chars: int = 4000) -> dict:
        started = time.time()
        total_indexed = 0
        total_seen = 0
        batches = 0
        last: dict = {}
        for _ in range(max_batches):
            last = self.index_notes(batch_size, project, category, max_chars)
            batches += 1
            total_indexed += int(last["indexed"])
            total_seen += int(last["seen"])
            if int(last["indexed"]) == 0:
                break
        progress = self.progress(project, category)
        result = {
            "batches": batches,
            "indexed": total_indexed,
            "seen": total_seen,
            "last": last,
            "progress": progress,
        }
        self.audit.record(AuditEvent(action="project_embeddings.index_batches", component="memory", params=result, duration_ms=int((time.time() - started) * 1000)))
        return result

    def run_worker(
        self,
        batch_size: int = 25,
        max_batches: int = 10,
        max_seconds: int = 300,
        project: str | None = None,
        category: str | None = None,
        max_chars: int = 4000,
        history_path: str | Path | None = None,
    ) -> dict:
        started = time.time()
        total_indexed = 0
        total_seen = 0
        batches = 0
        stop_reason = "max_batches"
        last: dict = {}
        for _ in range(max_batches):
            if time.time() - started >= max_seconds:
                stop_reason = "max_seconds"
                break
            last = self.index_notes(batch_size, project, category, max_chars)
            batches += 1
            total_indexed += int(last["indexed"])
            total_seen += int(last["seen"])
            if int(last["indexed"]) == 0:
                stop_reason = "no_pending"
                break
        progress = self.progress(project, category)
        result = {
            "started_at": started,
            "duration_ms": int((time.time() - started) * 1000),
            "batches": batches,
            "indexed": total_indexed,
            "seen": total_seen,
            "stop_reason": stop_reason,
            "last": last,
            "progress": progress,
        }
        self.audit.record(AuditEvent(action="project_embeddings.worker", component="memory", params=result, duration_ms=result["duration_ms"]))
        if history_path:
            self._append_worker_history(history_path, result)
        return result

    def progress(self, project: str | None = None, category: str | None = None) -> dict:
        notes = self._all_note_rows(project, category)
        embedded = self._embedding_hashes(project, category)
        indexed = 0
        stale = 0
        for row in notes:
            current = embedded.get(row["path"])
            if current == row["content_hash"]:
                indexed += 1
            elif current is not None:
                stale += 1
        total = len(notes)
        pending = total - indexed
        return {
            "total": total,
            "indexed": indexed,
            "stale": stale,
            "pending": pending,
            "percent": round((indexed / total) * 100, 2) if total else 100.0,
            "model": self.provider.model,
        }

    def search(self, query: str, limit: int = 10, project: str | None = None, category: str | None = None) -> list[ProjectEmbeddingResult]:
        started = time.time()
        rows = self._embedding_rows(project, category)
        if not rows:
            self.audit.record(AuditEvent(action="project_embeddings.search", component="memory", params={"query": query, "count": 0}, duration_ms=int((time.time() - started) * 1000)))
            return []
        query_vector = self.provider.embed(query)
        results = [
            ProjectEmbeddingResult(row["path"], row["title"], row["project"], row["category"], _cosine(query_vector, json.loads(row["vector_json"])), "project_note_embeddings")
            for row in rows
        ]
        ordered = sorted(results, key=lambda item: item.score, reverse=True)[:limit]
        self.audit.record(AuditEvent(action="project_embeddings.search", component="memory", params={"query": query, "count": len(ordered)}, duration_ms=int((time.time() - started) * 1000)))
        return ordered

    def _candidate_rows(self, limit: int, project: str | None, category: str | None) -> list[sqlite3.Row]:
        rows = self._all_note_rows(project, category)
        embedded = self._embedding_hashes(project, category)
        return [row for row in rows if embedded.get(row["path"]) != row["content_hash"]][:limit]

    def _all_note_rows(self, project: str | None, category: str | None) -> list[sqlite3.Row]:
        if not self.project_db.exists():
            return []
        where = []
        params: list[str] = []
        if project:
            where.append("project LIKE ?")
            params.append(f"%{project}%")
        if category:
            where.append("category = ?")
            params.append(category)
        sql = "SELECT path,title,project,category,tags,content_hash,modified_at FROM indexed_notes"
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY modified_at DESC"
        with sqlite3.connect(self.project_db) as conn:
            conn.row_factory = sqlite3.Row
            return conn.execute(sql, params).fetchall()

    def _embedding_hashes(self, project: str | None, category: str | None) -> dict[str, str]:
        where = ["model = ?"]
        params: list[str] = [self.provider.model]
        if project:
            where.append("project LIKE ?")
            params.append(f"%{project}%")
        if category:
            where.append("category = ?")
            params.append(category)
        with sqlite3.connect(self.embedding_db) as conn:
            return dict(conn.execute(f"SELECT path, content_hash FROM project_note_embeddings WHERE {' AND '.join(where)}", params).fetchall())

    def _embedding_rows(self, project: str | None, category: str | None) -> list[sqlite3.Row]:
        where = ["model = ?"]
        params: list[str] = [self.provider.model]
        if project:
            where.append("project LIKE ?")
            params.append(f"%{project}%")
        if category:
            where.append("category = ?")
            params.append(category)
        with sqlite3.connect(self.embedding_db) as conn:
            conn.row_factory = sqlite3.Row
            return conn.execute(
                f"SELECT path,title,project,category,vector_json FROM project_note_embeddings WHERE {' AND '.join(where)}",
                params,
            ).fetchall()

    def _append_worker_history(self, history_path: str | Path, result: dict) -> None:
        path = Path(history_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")


def read_project_embedding_worker_history(history_path: str | Path, limit: int = 20) -> list[dict]:
    path = Path(history_path)
    if not path.exists():
        return []
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return rows[-limit:]
