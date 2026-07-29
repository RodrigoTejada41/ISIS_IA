from __future__ import annotations

import json
import subprocess
import sys

from aurora.automation.action_audit import UIActionAuditLogger
from aurora.automation.ui import UIAction, UIActionResult, UIActionStatus, UIActionType


def test_action_audit_writes_jsonl(tmp_path) -> None:
    logger = UIActionAuditLogger(tmp_path / "ui_actions.jsonl")
    result = UIActionResult(UIActionStatus.EXECUTED, UIAction(UIActionType.CLICK, "salvar"), "mock execution only")

    record = logger.record(result, approved=True, real_execution=False)

    assert record.status == "EXECUTED"
    assert logger.tail(1)[0]["target"] == "salvar"


def test_ui_permissions_status_cli_outputs_safe_defaults() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "aurora.cli", "ui-permissions-status"],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(completed.stdout)

    assert payload["real_ui_execution_enabled"] is False
    assert payload["approval_per_action"] is True
    assert payload["screen_real_capture_enabled"] is False


def test_ui_mock_action_cli_records_audit() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "aurora.cli", "ui-mock-action", "salvar formulario", "--approve"],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(completed.stdout)

    assert payload["status"] == "EXECUTED"


def test_ui_action_audit_cli_outputs_list() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "aurora.cli", "ui-action-audit", "--limit", "5"],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(completed.stdout)

    assert isinstance(payload, list)
