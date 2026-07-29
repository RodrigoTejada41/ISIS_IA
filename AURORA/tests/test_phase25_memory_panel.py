from __future__ import annotations

import json
import subprocess
import sys

from aurora.core.runtime import AuroraRuntime
from aurora.ui.memory_panel import MemoryPanelService


def test_memory_panel_proposes_and_confirms(tmp_path) -> None:
    runtime = AuroraRuntime(tmp_path)
    service = MemoryPanelService(runtime)

    proposed = service.propose("registrar decisao local")
    confirmed = service.set_status(proposed.id or "", "CONFIRMED")
    rows = service.list_records("CONFIRMED")

    assert proposed.ok is True
    assert confirmed.ok is True
    assert any(row.id == proposed.id for row in rows)


def test_memory_panel_rejects_empty_content(tmp_path) -> None:
    result = MemoryPanelService(AuroraRuntime(tmp_path)).propose(" ")

    assert result.ok is False
    assert result.reason == "content required"


def test_ui_memory_propose_cli_outputs_json(tmp_path) -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "aurora.cli", "--root", str(tmp_path), "ui-memory-propose", "nota proposta"],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(completed.stdout)

    assert payload["ok"] is True
    assert payload["id"]


def test_ui_memory_list_cli_outputs_json(tmp_path) -> None:
    subprocess.run(
        [sys.executable, "-m", "aurora.cli", "--root", str(tmp_path), "ui-memory-propose", "nota proposta"],
        check=True,
        capture_output=True,
        text=True,
    )
    completed = subprocess.run(
        [sys.executable, "-m", "aurora.cli", "--root", str(tmp_path), "ui-memory-list", "--status", "PROPOSED"],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(completed.stdout)

    assert isinstance(payload, list)
    assert payload[0]["status"] == "PROPOSED"
