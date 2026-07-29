from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from aurora.core.audit import AuditEvent, AuditLogger


LINK_RE = re.compile(r"\[\[([^\]]+)\]\]")
TAG_RE = re.compile(r"(?<!\w)#([\w\-/]+)", re.UNICODE)
CHECKBOX_RE = re.compile(r"^\s*[-*]\s+\[( |x|X)\]\s+(.*)$", re.MULTILINE)


@dataclass(frozen=True, slots=True)
class ObsidianNote:
    path: str
    title: str
    frontmatter: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    links: list[str] = field(default_factory=list)
    backlinks: list[str] = field(default_factory=list)
    checklist_total: int = 0
    checklist_done: int = 0
    content_hash: str = ""
    modified_at: float = 0.0


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_scalar(value: str) -> Any:
    value = value.strip().strip('"').strip("'")
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    if value.startswith("[") and value.endswith("]"):
        return [item.strip().strip('"').strip("'") for item in value[1:-1].split(",") if item.strip()]
    return value


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    raw = text[3:end].strip()
    body = text[end + 4 :]
    data: dict[str, Any] = {}
    current_key: str | None = None
    for line in raw.splitlines():
        if not line.strip():
            continue
        if line.startswith("  - ") and current_key:
            if not isinstance(data.get(current_key), list):
                data[current_key] = []
            data[current_key].append(parse_scalar(line[4:]))
            continue
        if ":" in line:
            key, value = line.split(":", 1)
            current_key = key.strip()
            data[current_key] = parse_scalar(value) if value.strip() else []
    return data, body


def normalize_link(raw: str) -> str:
    return raw.split("|", 1)[0].split("#", 1)[0].strip()


class ObsidianConnector:
    def __init__(self, vault: str | Path, audit: AuditLogger) -> None:
        self.vault = Path(vault)
        self.audit = audit

    def read_note(self, path: str | Path) -> ObsidianNote:
        note_path = Path(path)
        data = note_path.read_bytes()
        text = data.decode("utf-8", errors="ignore")
        frontmatter, body = parse_frontmatter(text)
        tags = sorted(set(TAG_RE.findall(body)))
        fm_tags = frontmatter.get("tags")
        if isinstance(fm_tags, list):
            tags = sorted(set(tags + [str(tag) for tag in fm_tags]))
        links = [normalize_link(item) for item in LINK_RE.findall(body)]
        checkboxes = CHECKBOX_RE.findall(body)
        return ObsidianNote(
            path=str(note_path),
            title=note_path.stem,
            frontmatter=frontmatter,
            tags=tags,
            links=links,
            checklist_total=len(checkboxes),
            checklist_done=sum(1 for state, _ in checkboxes if state.lower() == "x"),
            content_hash=sha256_bytes(data),
            modified_at=note_path.stat().st_mtime,
        )

    def scan(self, max_files: int | None = None) -> list[ObsidianNote]:
        started = time.time()
        notes: list[ObsidianNote] = []
        for path in self.vault.rglob("*.md"):
            notes.append(self.read_note(path))
            if max_files and len(notes) >= max_files:
                break
        backlinks: dict[str, list[str]] = {Path(note.path).stem.lower(): [] for note in notes}
        path_by_stem = {Path(note.path).stem.lower(): note.path for note in notes}
        for note in notes:
            for link in note.links:
                target = Path(link).stem.lower()
                if target in backlinks:
                    backlinks[target].append(note.path)
        enriched = [
            ObsidianNote(**{**asdict(note), "backlinks": sorted(set(backlinks.get(Path(note.path).stem.lower(), [])))})
            for note in notes
        ]
        self.audit.record(AuditEvent(action="obsidian.scan", component="obsidian", params={"notes": len(enriched)}, duration_ms=int((time.time() - started) * 1000)))
        return enriched


class ObsidianMetadataStore:
    def __init__(self, db_path: str | Path, audit: AuditLogger) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.audit = audit
        self._init()

    def _init(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS obsidian_notes (
                    path TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    frontmatter_json TEXT NOT NULL,
                    tags_json TEXT NOT NULL,
                    links_json TEXT NOT NULL,
                    backlinks_json TEXT NOT NULL,
                    checklist_total INTEGER NOT NULL,
                    checklist_done INTEGER NOT NULL,
                    content_hash TEXT NOT NULL,
                    modified_at REAL NOT NULL,
                    indexed_at REAL NOT NULL,
                    version INTEGER NOT NULL
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_obsidian_title ON obsidian_notes(title)")

    def upsert_many(self, notes: list[ObsidianNote]) -> dict:
        created = updated = unchanged = 0
        with sqlite3.connect(self.db_path) as conn:
            for note in notes:
                existing = conn.execute("SELECT content_hash, version FROM obsidian_notes WHERE path = ?", (note.path,)).fetchone()
                if existing and existing[0] == note.content_hash:
                    unchanged += 1
                    continue
                version = int(existing[1]) + 1 if existing else 1
                conn.execute(
                    """
                    INSERT OR REPLACE INTO obsidian_notes
                    (path, title, frontmatter_json, tags_json, links_json, backlinks_json, checklist_total, checklist_done, content_hash, modified_at, indexed_at, version)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        note.path,
                        note.title,
                        json.dumps(note.frontmatter, ensure_ascii=False),
                        json.dumps(note.tags, ensure_ascii=False),
                        json.dumps(note.links, ensure_ascii=False),
                        json.dumps(note.backlinks, ensure_ascii=False),
                        note.checklist_total,
                        note.checklist_done,
                        note.content_hash,
                        note.modified_at,
                        time.time(),
                        version,
                    ),
                )
                created += int(existing is None)
                updated += int(existing is not None)
        result = {"created": created, "updated": updated, "unchanged": unchanged, "total": len(notes)}
        self.audit.record(AuditEvent(action="obsidian.metadata.upsert", component="obsidian", params=result))
        return result

    def stats(self) -> dict:
        with sqlite3.connect(self.db_path) as conn:
            notes = conn.execute("SELECT COUNT(*) FROM obsidian_notes").fetchone()[0]
            checklists = conn.execute("SELECT SUM(checklist_total), SUM(checklist_done) FROM obsidian_notes").fetchone()
        return {"notes": notes, "checklist_total": checklists[0] or 0, "checklist_done": checklists[1] or 0}
