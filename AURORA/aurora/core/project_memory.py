from __future__ import annotations

import hashlib
import re
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path

from aurora.core.audit import AuditEvent, AuditLogger


PROJECT_HINTS = {"Projetos", "projetos", "11_Projetos", "projects"}


@dataclass(frozen=True, slots=True)
class IndexedNote:
    path: str
    title: str
    project: str
    category: str
    tags: str
    links_count: int
    content_hash: str
    modified_at: float


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def classify_note(text: str, path: Path) -> str:
    lower = f"{path.name}\n{text[:4000]}".lower()
    if "bug" in lower or "erro" in lower:
        return "BUG"
    if "solucao" in lower or "solução" in lower:
        return "SOLUTION"
    if "decisao" in lower or "decisão" in lower or "adr" in lower:
        return "DECISION"
    if "- [ ]" in lower or "- [x]" in lower or "tarefa" in lower:
        return "TASK"
    if "preferencia" in lower or "preferência" in lower:
        return "PREFERENCE"
    if "requisito" in lower:
        return "REQUIREMENT"
    if "arquitetura" in lower:
        return "ARCHITECTURE"
    return "DOCUMENTATION"


def infer_project(vault: Path, path: Path) -> str:
    relative = path.relative_to(vault)
    parts = relative.parts
    if len(parts) >= 2 and parts[0] in PROJECT_HINTS:
        return parts[1]
    return parts[0] if parts else "CEREBRO_VIVO"


def extract_tags(text: str) -> str:
    tags = sorted(set(re.findall(r"(?<!\w)#([\w\-/]+)", text, flags=re.UNICODE)))
    return ",".join(tags[:50])


class ProjectMemoryIndex:
    def __init__(self, db_path: str | Path, audit: AuditLogger) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.audit = audit
        self._init()

    def _init(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS indexed_notes (
                    path TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    project TEXT NOT NULL,
                    category TEXT NOT NULL,
                    tags TEXT NOT NULL,
                    links_count INTEGER NOT NULL,
                    content_hash TEXT NOT NULL,
                    modified_at REAL NOT NULL,
                    indexed_at REAL NOT NULL,
                    version INTEGER NOT NULL
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_notes_project ON indexed_notes(project)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_notes_category ON indexed_notes(category)")

    def upsert_note(self, note: IndexedNote) -> str:
        with sqlite3.connect(self.db_path) as conn:
            existing = conn.execute("SELECT content_hash, version FROM indexed_notes WHERE path = ?", (note.path,)).fetchone()
            if existing and existing[0] == note.content_hash:
                return "unchanged"
            version = int(existing[1]) + 1 if existing else 1
            conn.execute(
                """
                INSERT OR REPLACE INTO indexed_notes
                (path, title, project, category, tags, links_count, content_hash, modified_at, indexed_at, version)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (note.path, note.title, note.project, note.category, note.tags, note.links_count, note.content_hash, note.modified_at, time.time(), version),
            )
        return "updated" if existing else "created"

    def search(self, query: str, limit: int = 20) -> list[dict]:
        pattern = f"%{query}%"
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """
                SELECT * FROM indexed_notes
                WHERE title LIKE ? OR project LIKE ? OR tags LIKE ? OR category LIKE ?
                ORDER BY modified_at DESC
                LIMIT ?
                """,
                (pattern, pattern, pattern, pattern, limit),
            ).fetchall()
        result = [dict(row) for row in rows]
        self.audit.record(AuditEvent(action="project_memory.search", component="memory", params={"query": query, "count": len(result)}))
        return result

    def stats(self) -> dict:
        with sqlite3.connect(self.db_path) as conn:
            notes = conn.execute("SELECT COUNT(*) FROM indexed_notes").fetchone()[0]
            projects = conn.execute("SELECT COUNT(DISTINCT project) FROM indexed_notes").fetchone()[0]
            categories = dict(conn.execute("SELECT category, COUNT(*) FROM indexed_notes GROUP BY category").fetchall())
        return {"notes": notes, "projects": projects, "categories": categories}


class ObsidianReadOnlyIndexer:
    def __init__(self, vault: str | Path, index: ProjectMemoryIndex, audit: AuditLogger) -> None:
        self.vault = Path(vault)
        self.index = index
        self.audit = audit

    def index_markdown(self, max_files: int | None = None) -> dict:
        started = time.time()
        created = 0
        updated = 0
        unchanged = 0
        scanned = 0
        for path in self.vault.rglob("*.md"):
            scanned += 1
            text = path.read_text(encoding="utf-8", errors="ignore")
            note = IndexedNote(
                path=str(path),
                title=path.stem,
                project=infer_project(self.vault, path),
                category=classify_note(text, path),
                tags=extract_tags(text),
                links_count=len(re.findall(r"\[\[([^\]]+)\]\]", text)),
                content_hash=sha256_text(text),
                modified_at=path.stat().st_mtime,
            )
            status = self.index.upsert_note(note)
            created += int(status == "created")
            updated += int(status == "updated")
            unchanged += int(status == "unchanged")
            if max_files and scanned >= max_files:
                break
        result = {"scanned": scanned, "created": created, "updated": updated, "unchanged": unchanged, "duration_ms": int((time.time() - started) * 1000)}
        self.audit.record(AuditEvent(action="obsidian.index_markdown", component="obsidian", params=result))
        return result
