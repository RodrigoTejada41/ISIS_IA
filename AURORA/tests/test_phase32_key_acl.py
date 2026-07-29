from __future__ import annotations

import json
import subprocess
import sys

from aurora.core.key_acl import KeyAclInspector


def test_key_acl_missing_file_reports_not_exists(tmp_path) -> None:
    status = KeyAclInspector().inspect(tmp_path / "missing.json")

    assert status.exists is False
    assert status.restricted is False


def test_key_acl_existing_file_reports_status(tmp_path) -> None:
    key = tmp_path / "key.json"
    key.write_text("{}", encoding="utf-8")

    status = KeyAclInspector().inspect(key)

    assert status.exists is True
    assert isinstance(status.restricted, bool)


def test_signature_key_acl_status_cli_outputs_json() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "aurora.cli", "signature-key-acl-status"],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(completed.stdout)

    assert payload["exists"] is True
    assert "restricted" in payload
