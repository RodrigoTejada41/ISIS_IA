from __future__ import annotations

import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path

from aurora.core.audit import AuditEvent, AuditLogger


NOISE_NAMES = {
    ".git",
    ".github",
    ".venv",
    "node_modules",
    "site-packages",
    "__pycache__",
    "dist",
    "build",
    "vendor",
    "packages",
}


@dataclass(frozen=True, slots=True)
class ProjectSummary:
    name: str
    notes: int
    decisions: int
    bugs: int
    tasks: int
    solutions: int
    latest_modified_at: float
    confidence: float
    status: str = "ACTIVE"


class ProjectCatalog:
    def __init__(self, db_path: str | Path, audit: AuditLogger) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.audit = audit
        self._init()

    def _init(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS project_catalog (
                    name TEXT PRIMARY KEY,
                    notes INTEGER NOT NULL,
                    decisions INTEGER NOT NULL,
                    bugs INTEGER NOT NULL,
                    tasks INTEGER NOT NULL,
                    solutions INTEGER NOT NULL,
                    latest_modified_at REAL NOT NULL,
                    confidence REAL NOT NULL,
                    status TEXT NOT NULL,
                    updated_at REAL NOT NULL
                )
                """
            )

    def consolidate_from_project_memory(self, project_memory_db: str | Path, min_notes: int = 3) -> dict:
        started = time.time()
        summaries: list[ProjectSummary] = []
        with sqlite3.connect(project_memory_db) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """
                SELECT project,
                       COUNT(*) notes,
                       SUM(CASE WHEN category='DECISION' THEN 1 ELSE 0 END) decisions,
                       SUM(CASE WHEN category='BUG' THEN 1 ELSE 0 END) bugs,
                       SUM(CASE WHEN category='TASK' THEN 1 ELSE 0 END) tasks,
                       SUM(CASE WHEN category='SOLUTION' THEN 1 ELSE 0 END) solutions,
                       MAX(modified_at) latest_modified_at
                FROM indexed_notes
                GROUP BY project
                """
            ).fetchall()
        for row in rows:
            name = row["project"]
            if not self._is_project_candidate(name, int(row["notes"]), min_notes):
                continue
            confidence = self._confidence(name, int(row["notes"]), int(row["decisions"]), int(row["bugs"]), int(row["tasks"]))
            summaries.append(
                ProjectSummary(
                    name=name,
                    notes=int(row["notes"]),
                    decisions=int(row["decisions"]),
                    bugs=int(row["bugs"]),
                    tasks=int(row["tasks"]),
                    solutions=int(row["solutions"]),
                    latest_modified_at=float(row["latest_modified_at"] or 0),
                    confidence=confidence,
                )
            )
        with sqlite3.connect(self.db_path) as conn:
            for item in summaries:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO project_catalog
                    (name, notes, decisions, bugs, tasks, solutions, latest_modified_at, confidence, status, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (item.name, item.notes, item.decisions, item.bugs, item.tasks, item.solutions, item.latest_modified_at, item.confidence, item.status, time.time()),
                )
        result = {"projects": len(summaries), "duration_ms": int((time.time() - started) * 1000)}
        self.audit.record(AuditEvent(action="project_catalog.consolidate", component="memory", params=result))
        return result

    def list_projects(self, limit: int = 50) -> list[dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM project_catalog ORDER BY confidence DESC, notes DESC LIMIT ?", (limit,)).fetchall()
        return [dict(row) for row in rows]

    def find_project(self, name: str) -> dict | None:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM project_catalog WHERE name = ?", (name,)).fetchone()
        return dict(row) if row else None

    def _is_project_candidate(self, name: str, notes: int, min_notes: int) -> bool:
        clean = name.strip()
        if notes < min_notes:
            return False
        if clean.lower() in NOISE_NAMES:
            return False
        if clean.endswith(".dist-info") or clean.endswith(".data"):
            return False
        if len(clean) <= 1:
            return False
        return True

    def _confidence(self, name: str, notes: int, decisions: int, bugs: int, tasks: int) -> float:
        score = min(0.6, notes / 1000)
        score += min(0.15, decisions / 50)
        score += min(0.15, bugs / 100)
        score += min(0.1, tasks / 100)
        if name in {"ISIS", "CEREBRO_VIVO", "Projetos", "MoviSys", "MoviPDV", "Movi_commanda"}:
            score += 0.2
        return round(min(score, 1.0), 3)
