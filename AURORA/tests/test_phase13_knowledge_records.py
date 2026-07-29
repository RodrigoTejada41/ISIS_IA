import sqlite3

from aurora.core.audit import AuditLogger
from aurora.core.knowledge_records import BugRecord, DecisionRecord, KnowledgeRecordStore


def test_add_and_search_decision_and_bug(tmp_path):
    store = KnowledgeRecordStore(tmp_path / "knowledge.sqlite", AuditLogger(tmp_path / "audit.jsonl"))

    store.add_decision(DecisionRecord("ISIS", "Usar SQLite", "offline", "a.md"))
    store.add_bug(BugRecord("ISIS", "Erro de link", "link quebrado", "b.md"))

    assert store.search_decisions("SQLite")[0]["project"] == "ISIS"
    assert store.search_bugs("link")[0]["title"] == "Erro de link"
    assert store.stats() == {"decisions": 1, "bugs": 1}


def test_import_from_project_memory_is_idempotent(tmp_path):
    memory_db = tmp_path / "project_memory.sqlite"
    with sqlite3.connect(memory_db) as conn:
        conn.execute(
            """
            CREATE TABLE indexed_notes (
                path TEXT PRIMARY KEY, title TEXT, project TEXT, category TEXT,
                tags TEXT, links_count INTEGER, content_hash TEXT, modified_at REAL,
                indexed_at REAL, version INTEGER
            )
            """
        )
        conn.executemany(
            "INSERT INTO indexed_notes VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                ("d.md", "Decisao A", "ISIS", "DECISION", "", 0, "1", 1, 1, 1),
                ("b.md", "Bug A", "ISIS", "BUG", "", 0, "2", 1, 1, 1),
            ],
        )
    store = KnowledgeRecordStore(tmp_path / "knowledge.sqlite", AuditLogger(tmp_path / "audit.jsonl"))

    store.import_from_project_memory(memory_db)
    store.import_from_project_memory(memory_db)

    assert store.stats() == {"decisions": 1, "bugs": 1}
