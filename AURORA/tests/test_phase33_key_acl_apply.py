from __future__ import annotations

import json
import subprocess
import sys

from aurora.core.key_acl import KeyAclManager


def test_key_acl_apply_dry_run(tmp_path) -> None:
    key = tmp_path / "key.json"
    key.write_text("{}", encoding="utf-8")

    result = KeyAclManager().apply_restricted(key, apply=False)

    assert result.applied is False
    assert result.success is True
    assert any("/inheritance:r" in command for command in result.commands)


def test_key_acl_rollback_dry_run(tmp_path) -> None:
    result = KeyAclManager().rollback(tmp_path / "key.json", tmp_path / "acl.txt", apply=False)

    assert result.applied is False
    assert result.success is True
    assert result.commands[0][2] == "/restore"


def test_signature_key_acl_apply_cli_dry_run_outputs_json() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "aurora.cli", "signature-key-acl-apply"],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(completed.stdout)

    assert payload["applied"] is False
    assert payload["success"] is True
