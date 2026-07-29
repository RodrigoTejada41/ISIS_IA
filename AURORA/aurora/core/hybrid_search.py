from __future__ import annotations

import json
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path

from aurora.core.audit import AuditEvent, AuditLogger


@dataclass(frozen=True, slots=True)
class SearchResult:
    path: str
    title: str
    source: str
    score: float
    project: str = ""
    category: str = ""
    tags: list[str] | None = None
    reason: str = ""


class HybridSearchService:
    def __init__(self, project_db: str | Path, obsidian_db: str | Path, audit: AuditLogger) -> None:
        self.project_db = Path(project_db)
        self.obsidian_db = Path(obsidian_db)
        self.audit = audit

    def search(self, query: str, limit: int = 10, project: str | None = None, category: str | None = None) -> list[SearchResult]:
        started = time.time()
        terms = [term.lower() for term in query.split() if term.strip()]
        results: dict[str, SearchResult] = {}
        for item in self._search_project_memory(terms, limit * 3, project, category):
            results[item.path] = item
        if not project and not category:
            obsidian_items = self._search_obsidian_metadata(terms, limit * 3)
        else:
            obsidian_items = []
        for item in obsidian_items:
            existing = results.get(item.path)
            if existing:
                results[item.path] = SearchResult(
                    path=item.path,
                    title=item.title or existing.title,
                    source="hybrid",
                    score=existing.score + item.score,
                    project=existing.project,
                    category=existing.category,
                    tags=sorted(set((existing.tags or []) + (item.tags or []))),
                    reason=f"{existing.reason}; {item.reason}",
                )
            else:
                results[item.path] = item
        ordered = sorted(results.values(), key=lambda row: row.score, reverse=True)[:limit]
        self.audit.record(AuditEvent(action="hybrid_search.search", component="search", params={"query": query, "count": len(ordered)}, duration_ms=int((time.time() - started) * 1000)))
        return ordered

    def _score_text(self, terms: list[str], fields: dict[str, str]) -> tuple[float, list[str]]:
        score = 0.0
        reasons: list[str] = []
        weights = {"title": 5.0, "project": 3.0, "category": 2.0, "tags": 2.5, "links": 1.5}
        for name, text in fields.items():
            lower = text.lower()
            hits = sum(1 for term in terms if term in lower)
            if hits:
                score += hits * weights.get(name, 1.0)
                reasons.append(f"{name}:{hits}")
        return score, reasons

    def _search_project_memory(self, terms: list[str], limit: int, project: str | None, category: str | None) -> list[SearchResult]:
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
        sql = "SELECT path,title,project,category,tags,links_count FROM indexed_notes"
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY modified_at DESC LIMIT 5000"
        rows: list[SearchResult] = []
        with sqlite3.connect(self.project_db) as conn:
            conn.row_factory = sqlite3.Row
            for row in conn.execute(sql, params):
                score, reasons = self._score_text(terms, {"title": row["title"], "project": row["project"], "category": row["category"], "tags": row["tags"]})
                if score > 0:
                    rows.append(SearchResult(row["path"], row["title"], "project_memory", score, row["project"], row["category"], row["tags"].split(",") if row["tags"] else [], ",".join(reasons)))
        return sorted(rows, key=lambda item: item.score, reverse=True)[:limit]

    def _search_obsidian_metadata(self, terms: list[str], limit: int) -> list[SearchResult]:
        if not self.obsidian_db.exists():
            return []
        rows: list[SearchResult] = []
        with sqlite3.connect(self.obsidian_db) as conn:
            conn.row_factory = sqlite3.Row
            for row in conn.execute("SELECT path,title,tags_json,links_json,checklist_total FROM obsidian_notes ORDER BY modified_at DESC LIMIT 5000"):
                tags = json.loads(row["tags_json"])
                links = json.loads(row["links_json"])
                score, reasons = self._score_text(terms, {"title": row["title"], "tags": " ".join(tags), "links": " ".join(links)})
                if row["checklist_total"] and any(term in {"tarefa", "task", "checklist"} for term in terms):
                    score += 2
                    reasons.append("checklist")
                if score > 0:
                    rows.append(SearchResult(row["path"], row["title"], "obsidian", score, tags=tags, reason=",".join(reasons)))
        return sorted(rows, key=lambda item: item.score, reverse=True)[:limit]
