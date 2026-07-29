from aurora.core.assistant import IsisAssistantCore
from aurora.core.memory import MemoryRecord, MemoryStatus, MemoryType


def test_core_initializes_and_shutdown(tmp_path):
    core = IsisAssistantCore(tmp_path)

    health = core.initialize()
    core.shutdown("test")

    assert health["status"] in {"ok", "warning"}
    assert core.running is False
    assert any(event.name == "core.started" for event in core.events.history())
    assert any(event.name == "core.shutdown" for event in core.events.history())


def test_core_status_command_uses_tool_registry(tmp_path):
    core = IsisAssistantCore(tmp_path)
    core.initialize()

    result = core.handle_text("status")

    assert result.command_type == "status"
    assert result.output["obsidian_mode"] == "READ_ONLY"


def test_core_routes_model_command(tmp_path):
    core = IsisAssistantCore(tmp_path)
    core.initialize()

    result = core.handle_text("corrija este codigo em python")

    assert result.command_type == "model_route"
    assert result.profile == "CODING"
    assert result.model == "coding-local-mock"


def test_core_memory_command_uses_rag(tmp_path):
    core = IsisAssistantCore(tmp_path)
    core.initialize()
    memory_id = core.runtime.memory.add(MemoryRecord("ISIS usa configuracao central", MemoryType.CONFIRMED_FACT, "test", "tester"))
    core.runtime.memory.set_status(memory_id, MemoryStatus.CONFIRMED)

    result = core.handle_text("memoria: ISIS")

    assert result.command_type == "memory_search"
    assert memory_id in (result.used_memory_ids or [])


def test_core_rejects_command_before_initialize(tmp_path):
    core = IsisAssistantCore(tmp_path)

    try:
        core.handle_text("status")
    except RuntimeError as exc:
        assert "not running" in str(exc)
    else:
        raise AssertionError("expected runtime error")
