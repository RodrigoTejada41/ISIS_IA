from aurora.core.audit import AuditLogger
from aurora.core.memory import MemoryRecord, MemoryStatus, MemoryStore, MemoryType, RagService


def test_memory_lifecycle_and_text_search(tmp_path):
    audit = AuditLogger(tmp_path / "audit.jsonl")
    store = MemoryStore(tmp_path / "memory.sqlite", audit)

    memory_id = store.add(
        MemoryRecord(
            content="Projeto AURORA usa assistente local offline",
            type=MemoryType.PROJECT_KNOWLEDGE,
            origin="test",
            user="tester",
        )
    )
    store.set_status(memory_id, MemoryStatus.CONFIRMED)

    rows = store.search_text("AURORA")

    assert len(rows) == 1
    assert rows[0]["id"] == memory_id


def test_rag_context_records_used_memories(tmp_path):
    audit = AuditLogger(tmp_path / "audit.jsonl")
    store = MemoryStore(tmp_path / "memory.sqlite", audit)
    memory_id = store.add(MemoryRecord("AURORA tem roteador local", MemoryType.CONFIRMED_FACT, "test", "tester"))
    store.set_status(memory_id, MemoryStatus.CONFIRMED)

    context, ids = RagService(store, audit).build_context("AURORA")

    assert memory_id in ids
    assert "roteador local" in context
