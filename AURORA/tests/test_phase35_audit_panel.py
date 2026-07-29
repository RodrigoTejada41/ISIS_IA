from __future__ import annotations

import json
import subprocess
import sys

from aurora.core.runtime import AuroraRuntime
from aurora.ui.audit_panel import AuditPanelService, AuditPanelSnapshot


def test_audit_panel_snapshot(tmp_path) -> None:
    snapshot = AuditPanelService(AuroraRuntime(tmp_path)).snapshot()

    assert isinstance(snapshot, AuditPanelSnapshot)
    assert snapshot.ui_actions >= 0
    assert snapshot.privilege_events >= 0
    assert snapshot.memory_events >= 0


def test_ui_audit_snapshot_cli_outputs_json() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "aurora.cli", "ui-audit-snapshot"],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(completed.stdout)

    assert "report_integrity_ok" in payload
    assert "signature_key_restricted" in payload
    assert "report_history_count" in payload
