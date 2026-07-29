from __future__ import annotations

import json
import subprocess
import sys

from aurora.core.auth import AUTH_ENV_VAR, LocalAuthenticator


def test_local_auth_bootstrap_and_verify(monkeypatch, tmp_path) -> None:
    auth = LocalAuthenticator(tmp_path / "auth.json", iterations=1_000)
    monkeypatch.setenv(AUTH_ENV_VAR, "senha-local-forte")

    status = auth.bootstrap_from_env()

    assert status.configured is True
    assert auth.verify_env() is True
    assert "senha-local-forte" not in (tmp_path / "auth.json").read_text(encoding="utf-8")


def test_local_auth_rejects_missing_password(tmp_path) -> None:
    auth = LocalAuthenticator(tmp_path / "auth.json", iterations=1_000)

    try:
        auth.bootstrap_from_env()
    except PermissionError as exc:
        assert AUTH_ENV_VAR in str(exc)
    else:
        raise AssertionError("expected PermissionError")


def test_auth_status_cli_outputs_json() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "aurora.cli", "auth-status"],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(completed.stdout)

    assert payload["env_var"] == AUTH_ENV_VAR
    assert "configured" in payload
