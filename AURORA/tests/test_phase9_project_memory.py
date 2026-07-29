from aurora.core.audit import AuditLogger
from aurora.core.project_memory import ObsidianReadOnlyIndexer, ProjectMemoryIndex, classify_note, infer_project


def test_classify_note_detects_decision(tmp_path):
    path = tmp_path / "decisao.md"

    assert classify_note("Decisao tecnica aprovada", path) == "DECISION"


def test_project_indexer_indexes_and_searches(tmp_path):
    vault = tmp_path / "vault"
    note = vault / "Projetos" / "ISIS" / "README.md"
    note.parent.mkdir(parents=True)
    note.write_text("# ISIS\n#tag [[Outra]]\nArquitetura do projeto", encoding="utf-8")
    audit = AuditLogger(tmp_path / "audit.jsonl")
    index = ProjectMemoryIndex(tmp_path / "project_memory.sqlite", audit)

    result = ObsidianReadOnlyIndexer(vault, index, audit).index_markdown()
    rows = index.search("ISIS")
    stats = index.stats()

    assert result["created"] == 1
    assert rows[0]["project"] == "ISIS"
    assert stats["notes"] == 1


def test_indexer_versions_changed_note(tmp_path):
    vault = tmp_path / "vault"
    note = vault / "Projetos" / "ISIS" / "README.md"
    note.parent.mkdir(parents=True)
    note.write_text("v1", encoding="utf-8")
    audit = AuditLogger(tmp_path / "audit.jsonl")
    index = ProjectMemoryIndex(tmp_path / "project_memory.sqlite", audit)
    indexer = ObsidianReadOnlyIndexer(vault, index, audit)

    indexer.index_markdown()
    note.write_text("v2 bug", encoding="utf-8")
    indexer.index_markdown()

    row = index.search("ISIS")[0]
    assert row["version"] == 2
    assert row["category"] == "BUG"
