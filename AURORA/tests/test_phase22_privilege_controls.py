from __future__ import annotations

import json
import subprocess
import sys

from aurora.core.auth import AUTH_ENV_VAR, LocalAuthenticator
from aurora.core.runtime import AuroraRuntime
from aurora.ui.privileges import PrivilegeControlService


def test_privilege_controls_block_without_auth(tmp_path) -> None:
    runtime = AuroraRuntime(tmp_path)
    service = PrivilegeControlService(runtime, LocalAuthenticator(tmp_path / "auth.json", iterations=1_000))

    state = service.state()
    result = service.change_profile("MEDIUM", "irrelevant")

    assert state.editable is False
    assert result.changed is False
    assert result.reason == "local authentication is not configured"


def test_privilege_controls_change_profile_with_password(monkeypatch, tmp_path) -> None:
    runtime = AuroraRuntime(tmp_path)
    authenticator = LocalAuthenticator(tmp_path / "auth.json", iterations=1_000)
    monkeypatch.setenv(AUTH_ENV_VAR, "senha-local-forte")
    authenticator.bootstrap_from_env()
    service = PrivilegeControlService(runtime, authenticator)

    result = service.change_profile("MEDIUM", "senha-local-forte")

    assert result.changed is True
    assert result.profile == "MEDIUM"


def test_ui_privileges_status_cli_outputs_json() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "aurora.cli", "ui-privileges-status"],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(completed.stdout)

    assert payload["current_profile"] in {"MEDIUM", "CONTROLLED", "TOTAL"}
    assert "available_profiles" in payload
    assert "editable" in payload
