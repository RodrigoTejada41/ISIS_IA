import json
import sqlite3

from aurora.core.audit import AuditLogger
from aurora.core.hybrid_search import HybridSearchService


def create_project_db(path):
    with sqlite3.connect(path) as conn:
        conn.execute(
            """
            CREATE TABLE indexed_notes (
                path TEXT PRIMARY KEY, title TEXT, project TEXT, category TEXT,
                tags TEXT, links_count INTEGER, content_hash TEXT, modified_at REAL,
                indexed_at REAL, version INTEGER
            )
            """
        )
        conn.execute(
            "INSERT INTO indexed_notes VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            ("a.md", "ISIS Arquitetura", "ISIS", "ARCHITECTURE", "core,offline", 1, "h", 2, 2, 1),
        )


def create_obsidian_db(path):
    with sqlite3.connect(path) as conn:
        conn.execute(
            """
            CREATE TABLE obsidian_notes (
                path TEXT PRIMARY KEY, title TEXT, frontmatter_json TEXT, tags_json TEXT,
                links_json TEXT, backlinks_json TEXT, checklist_total INTEGER,
                checklist_done INTEGER, content_hash TEXT, modified_at REAL,
                indexed_at REAL, version INTEGER
            )
            """
        )
        conn.execute(
            "INSERT INTO obsidian_notes VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            ("a.md", "ISIS Arquitetura", "{}", json.dumps(["core"]), json.dumps(["Memoria"]), "[]", 0, 0, "h", 2, 2, 1),
        )


def test_hybrid_search_merges_scores(tmp_path):
    project_db = tmp_path / "project.sqlite"
    obsidian_db = tmp_path / "obsidian.sqlite"
    create_project_db(project_db)
    create_obsidian_db(obsidian_db)
    service = HybridSearchService(project_db, obsidian_db, AuditLogger(tmp_path / "audit.jsonl"))

    result = service.search("ISIS core", limit=5)

    assert len(result) == 1
    assert result[0].source == "hybrid"
    assert result[0].score > 5


def test_hybrid_search_filters_project(tmp_path):
    project_db = tmp_path / "project.sqlite"
    obsidian_db = tmp_path / "obsidian.sqlite"
    create_project_db(project_db)
    create_obsidian_db(obsidian_db)
    service = HybridSearchService(project_db, obsidian_db, AuditLogger(tmp_path / "audit.jsonl"))

    assert service.search("ISIS", project="OUTRO") == []
