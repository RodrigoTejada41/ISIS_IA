import sqlite3

from aurora.core.audit import AuditLogger
from aurora.core.project_catalog import ProjectCatalog


def create_memory_db(path):
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
        rows = [
            ("1.md", "a", "ISIS", "DECISION", "", 0, "1", 1, 1, 1),
            ("2.md", "b", "ISIS", "BUG", "", 0, "2", 2, 2, 1),
            ("3.md", "c", "ISIS", "TASK", "", 0, "3", 3, 3, 1),
            ("4.md", "d", "node_modules", "DOCUMENTATION", "", 0, "4", 4, 4, 1),
        ]
        conn.executemany("INSERT INTO indexed_notes VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", rows)


def test_project_catalog_consolidates_real_candidates(tmp_path):
    memory_db = tmp_path / "memory.sqlite"
    catalog_db = tmp_path / "catalog.sqlite"
    create_memory_db(memory_db)
    catalog = ProjectCatalog(catalog_db, AuditLogger(tmp_path / "audit.jsonl"))

    result = catalog.consolidate_from_project_memory(memory_db, min_notes=2)
    projects = catalog.list_projects()

    assert result["projects"] == 1
    assert projects[0]["name"] == "ISIS"
    assert projects[0]["decisions"] == 1
    assert catalog.find_project("ISIS") is not None
