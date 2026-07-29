import subprocess
import sys

from aurora.core.audit import AuditLogger
from aurora.core.embeddings import MemoryEmbeddingIndex
from aurora.core.memory import MemoryRecord, MemoryStatus, MemoryStore, MemoryType


class FakeEmbeddingProvider:
    model = "fake-embed"

    def embed(self, text: str) -> list[float]:
        lower = text.lower()
        return [
            1.0 if "aurora" in lower else 0.0,
            1.0 if "sqlite" in lower else 0.0,
            1.0 if "voz" in lower else 0.0,
        ]


def test_memory_embedding_index_searches_semantically(tmp_path):
    audit = AuditLogger(tmp_path / "audit.jsonl")
    store = MemoryStore(tmp_path / "memory.sqlite", audit)
    first = store.add(MemoryRecord("AURORA usa SQLite local", MemoryType.CONFIRMED_FACT, "test", "local", status=MemoryStatus.CONFIRMED))
    store.add(MemoryRecord("Modulo de voz usa mock", MemoryType.CONFIRMED_FACT, "test", "local", status=MemoryStatus.CONFIRMED))

    index = MemoryEmbeddingIndex(tmp_path / "memory.sqlite", tmp_path / "embeddings.sqlite", audit, FakeEmbeddingProvider())
    result = index.index_confirmed()
    rows = index.search("banco sqlite da aurora")

    assert result["indexed"] == 2
    assert rows[0].id == first
    assert rows[0].score > 0


def test_memory_semantic_cli_with_empty_index_outputs_list(tmp_path):
    result = subprocess.run(
        [sys.executable, "-m", "aurora.cli", "--root", str(tmp_path), "memory-semantic-search", "aurora"],
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode == 0
    assert result.stdout.strip() == "[]"
