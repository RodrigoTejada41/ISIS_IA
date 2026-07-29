from __future__ import annotations

import json
import subprocess
import sys

from aurora.automation.ui import UIAction, UIActionStatus, UIActionType, UIAutomationService


def test_ui_action_requires_approval() -> None:
    service = UIAutomationService()
    action = UIAction(UIActionType.CLICK, "salvar")

    result = service.execute(action, approved=False)

    assert result.status == UIActionStatus.BLOCKED
    assert result.reason == "approval required"


def test_ui_action_executes_as_mock_when_approved() -> None:
    service = UIAutomationService()
    action = UIAction(UIActionType.CLICK, "salvar")

    result = service.execute(action, approved=True)

    assert result.status == UIActionStatus.EXECUTED
    assert result.reason == "mock execution only"


def test_ui_action_blocks_sensitive_target() -> None:
    service = UIAutomationService()
    action = UIAction(UIActionType.CLICK, "banco confirmar pagamento")

    result = service.execute(action, approved=True)

    assert result.status == UIActionStatus.BLOCKED


def test_ui_plan_cli_outputs_pending_action() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "aurora.cli", "ui-plan", "salvar formulario"],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(completed.stdout)

    assert payload[0]["action_type"] == "CLICK"
    assert payload[0]["requires_approval"] is True
