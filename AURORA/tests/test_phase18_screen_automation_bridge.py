from __future__ import annotations

import json
import subprocess
import sys

from aurora.automation.screen_bridge import ScreenAutomationBridge
from aurora.automation.ui import UIActionStatus, UIActionType
from aurora.perception.screen import MockScreenProvider


def test_bridge_suggests_click_from_detected_button() -> None:
    frame = MockScreenProvider("Campo email\nBotao salvar").capture()

    suggestion = ScreenAutomationBridge().suggest(frame, "salvar formulario")

    assert suggestion.action.action_type == UIActionType.CLICK
    assert suggestion.action.target == "Botao salvar"
    assert suggestion.confidence >= 0.9


def test_bridge_blocks_low_confidence_fallback() -> None:
    frame = MockScreenProvider("Campo email").capture()

    result = ScreenAutomationBridge().suggest_and_execute_mock(frame, "abrir relatorio", approved=True)

    assert result.status == UIActionStatus.BLOCKED
    assert result.reason == "low confidence"


def test_bridge_requires_approval_for_matched_action() -> None:
    frame = MockScreenProvider("Botao salvar").capture()

    result = ScreenAutomationBridge().suggest_and_execute_mock(frame, "salvar", approved=False)

    assert result.status == UIActionStatus.BLOCKED
    assert result.reason == "approval required"


def test_screen_ui_suggest_cli_outputs_json() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "aurora.cli", "screen-ui-suggest", "salvar", "--text", "Botao salvar", "--approve"],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(completed.stdout)

    assert payload["suggestion"]["confidence"] >= 0.9
    assert payload["result"]["status"] == "EXECUTED"
