import sqlite3
import subprocess
import sys

from aurora.core.audit import AuditLogger
from aurora.core.config import AuroraConfig, ConfigStore
from aurora.core.embeddings import ProjectEmbeddingIndex, read_project_embedding_worker_history
from aurora.core.project_memory import IndexedNote, ProjectMemoryIndex, sha256_text


class FakeEmbeddingProvider:
    model = "fake-embed"

    def embed(self, text: str) -> list[float]:
        lower = text.lower()
        return [
            1.0 if "aurora" in lower else 0.0,
            1.0 if "obsidian" in lower else 0.0,
            1.0 if "sqlite" in lower else 0.0,
        ]


def test_project_embedding_index_reads_notes_readonly(tmp_path):
    vault = tmp_path / "vault"
    note = vault / "Projetos" / "AURORA" / "memoria.md"
    note.parent.mkdir(parents=True)
    text = "AURORA integra Obsidian com SQLite local"
    note.write_text(text, encoding="utf-8")

    audit = AuditLogger(tmp_path / "audit.jsonl")
    project_db = tmp_path / "project_memory.sqlite"
    project_index = ProjectMemoryIndex(project_db, audit)
    project_index.upsert_note(
        IndexedNote(
            path=str(note),
            title="memoria",
            project="AURORA",
            category="DOCUMENTATION",
            tags="local",
            links_count=0,
            content_hash=sha256_text(text),
            modified_at=note.stat().st_mtime,
        )
    )

    embed = ProjectEmbeddingIndex(project_db, tmp_path / "project_embeddings.sqlite", audit, FakeEmbeddingProvider())
    result = embed.index_notes(limit=10)
    rows = embed.search("obsidian sqlite", limit=1)

    assert result["indexed"] == 1
    assert rows[0].path == str(note)
    assert rows[0].score > 0
    assert note.read_text(encoding="utf-8") == text


def test_project_embedding_progress_advances_past_indexed_notes(tmp_path):
    vault = tmp_path / "vault"
    audit = AuditLogger(tmp_path / "audit.jsonl")
    project_db = tmp_path / "project_memory.sqlite"
    project_index = ProjectMemoryIndex(project_db, audit)

    for idx in range(3):
        note = vault / f"n{idx}.md"
        note.parent.mkdir(parents=True, exist_ok=True)
        text = f"AURORA nota {idx} com SQLite"
        note.write_text(text, encoding="utf-8")
        project_index.upsert_note(
            IndexedNote(
                path=str(note),
                title=note.stem,
                project="AURORA",
                category="DOCUMENTATION",
                tags="",
                links_count=0,
                content_hash=sha256_text(text),
                modified_at=note.stat().st_mtime + idx,
            )
        )

    embed = ProjectEmbeddingIndex(project_db, tmp_path / "project_embeddings.sqlite", audit, FakeEmbeddingProvider())

    first = embed.index_notes(limit=1)
    second = embed.index_notes(limit=1)
    progress = embed.progress()

    assert first["indexed"] == 1
    assert second["indexed"] == 1
    assert progress["indexed"] == 2
    assert progress["pending"] == 1


def test_project_embedding_worker_writes_history(tmp_path):
    vault = tmp_path / "vault"
    audit = AuditLogger(tmp_path / "audit.jsonl")
    project_db = tmp_path / "project_memory.sqlite"
    project_index = ProjectMemoryIndex(project_db, audit)
    history = tmp_path / "worker.jsonl"

    for idx in range(2):
        note = vault / f"worker-{idx}.md"
        note.parent.mkdir(parents=True, exist_ok=True)
        text = f"AURORA worker {idx}"
        note.write_text(text, encoding="utf-8")
        project_index.upsert_note(
            IndexedNote(
                path=str(note),
                title=note.stem,
                project="AURORA",
                category="DOCUMENTATION",
                tags="",
                links_count=0,
                content_hash=sha256_text(text),
                modified_at=note.stat().st_mtime + idx,
            )
        )

    embed = ProjectEmbeddingIndex(project_db, tmp_path / "project_embeddings.sqlite", audit, FakeEmbeddingProvider())
    result = embed.run_worker(batch_size=1, max_batches=5, max_seconds=60, history_path=history)
    rows = read_project_embedding_worker_history(history)

    assert result["indexed"] == 2
    assert result["stop_reason"] == "no_pending"
    assert rows[-1]["progress"]["indexed"] == 2


def test_project_semantic_cli_empty_index_outputs_list(tmp_path):
    config = AuroraConfig()
    config.paths.isis_root = str(tmp_path / "ISIS")
    ConfigStore(tmp_path / "data" / "config.json").save(config)
    isis_db = tmp_path / "ISIS" / "data" / "databases"
    isis_db.mkdir(parents=True)
    with sqlite3.connect(isis_db / "project_memory.sqlite") as conn:
        conn.execute(
            """
            CREATE TABLE indexed_notes (
              path TEXT PRIMARY KEY, title TEXT, project TEXT, category TEXT,
              tags TEXT, links_count INTEGER, content_hash TEXT, modified_at REAL,
              indexed_at REAL, version INTEGER
            )
            """
        )

    result = subprocess.run(
        [sys.executable, "-m", "aurora.cli", "--root", str(tmp_path), "project-semantic-search", "aurora"],
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode == 0
    assert result.stdout.strip() == "[]"
