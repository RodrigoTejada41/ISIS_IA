from __future__ import annotations

import json
import subprocess
import sys

import pytest

from aurora.perception.screen import MockScreenProvider, ScreenPrivacyPolicy, ScreenVisionService, redact_sensitive_text


def test_redacts_sensitive_text() -> None:
    text = "senha=abc123\ntoken: secret\ncartao 4111 1111 1111 1111"

    redacted = redact_sensitive_text(text)

    assert "abc123" not in redacted
    assert "secret" not in redacted
    assert "4111" not in redacted
    assert redacted.count("[REDACTED]") >= 3


def test_screen_capture_requires_manual_confirmation() -> None:
    service = ScreenVisionService(MockScreenProvider("Botao salvar"), policy=ScreenPrivacyPolicy())

    with pytest.raises(PermissionError):
        service.capture_and_analyze(manual_confirmed=False)


def test_mock_analysis_detects_screen_elements() -> None:
    service = ScreenVisionService(
        MockScreenProvider("Menu Arquivo\nCampo email\nBotao salvar\nErro login invalido\nsenha=abc"),
        policy=ScreenPrivacyPolicy(),
    )

    result = service.capture_and_analyze(manual_confirmed=True)

    assert result.detected_menus
    assert result.detected_fields
    assert result.detected_buttons
    assert result.detected_errors
    assert result.privacy_applied is True
    assert "abc" not in result.redacted_text


def test_screen_mock_cli_outputs_json() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "aurora.cli", "screen-mock", "--text", "Campo login\nBotao entrar"],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(completed.stdout)

    assert payload["source"] == "mock"
    assert payload["detected_fields"]
    assert payload["detected_buttons"]
