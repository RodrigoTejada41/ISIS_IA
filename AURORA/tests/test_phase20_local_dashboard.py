from __future__ import annotations

import json
import subprocess
import sys

from aurora.core.runtime import AuroraRuntime
from aurora.ui.dashboard import DashboardSnapshot, build_dashboard_snapshot


def test_dashboard_snapshot_safe_defaults(tmp_path) -> None:
    snapshot = build_dashboard_snapshot(AuroraRuntime(tmp_path))

    assert isinstance(snapshot, DashboardSnapshot)
    assert snapshot.real_screen_capture_enabled is False
    assert snapshot.real_ui_execution_enabled is False
    assert snapshot.internet_enabled is False


def test_ui_snapshot_cli_outputs_json() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "aurora.cli", "ui-snapshot"],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(completed.stdout)

    assert payload["assistant_name"] == "ISIS"
    assert payload["real_screen_capture_enabled"] is False
    assert payload["real_ui_execution_enabled"] is False
    assert "ram_available_mb" in payload
    assert "project_notes_indexed" in payload
