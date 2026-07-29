from __future__ import annotations

import json
import subprocess
import sys

from aurora.core.runtime import AuroraRuntime
from aurora.ui.memory_panel import MemoryPanelService


def test_memory_export_json(tmp_path) -> None:
    runtime = AuroraRuntime(tmp_path)
    service = MemoryPanelService(runtime)
    service.propose("memoria exportavel")
    output = tmp_path / "memory.json"

    result = service.export_report(output, "PROPOSED", fmt="json")
    payload = json.loads(output.read_text(encoding="utf-8"))

    assert result.ok is True
    assert payload["count"] == 1
    assert payload["records"][0]["status"] == "PROPOSED"


def test_memory_export_markdown(tmp_path) -> None:
    runtime = AuroraRuntime(tmp_path)
    service = MemoryPanelService(runtime)
    service.propose("memoria markdown")
    output = tmp_path / "memory.md"

    result = service.export_report(output, "PROPOSED", fmt="md")

    assert result.ok is True
    assert "Memory Report" in output.read_text(encoding="utf-8")


def test_ui_memory_export_cli_outputs_file(tmp_path) -> None:
    subprocess.run(
        [sys.executable, "-m", "aurora.cli", "--root", str(tmp_path), "ui-memory-propose", "memoria cli"],
        check=True,
        capture_output=True,
        text=True,
    )
    output = tmp_path / "report.json"
    completed = subprocess.run(
        [sys.executable, "-m", "aurora.cli", "--root", str(tmp_path), "ui-memory-export", str(output), "--status", "PROPOSED"],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(completed.stdout)

    assert payload["ok"] is True
    assert output.exists()
