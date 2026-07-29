from __future__ import annotations

import json
import subprocess
import sys

from aurora.core.config import AuroraConfig, ConfigStore
from aurora.core.local_signature import LocalSignatureService


def write_isolated_config(root) -> None:
    config = AuroraConfig()
    isis_root = root / "ISIS"
    config.paths.isis_root = str(isis_root)
    config.paths.code_root = str(root)
    config.paths.models_dir = str(isis_root / "models")
    config.paths.backups_dir = str(isis_root / "backups")
    config.paths.logs_dir = str(isis_root / "logs")
    config.paths.cache_dir = str(isis_root / "data" / "cache")
    config.paths.temporary_dir = str(isis_root / "data" / "temporary")
    ConfigStore(root / "data" / "config.json").save(config)


def test_local_signature_signs_and_verifies(tmp_path) -> None:
    target = tmp_path / "report.json"
    target.write_text('{"ok":true}', encoding="utf-8")
    signature = tmp_path / "report.sig.json"
    service = LocalSignatureService(tmp_path / "key.json")

    result = service.sign_file(target, signature)

    assert result.ok is True
    assert service.verify_file(target, signature) is True
    assert "key" in (tmp_path / "key.json").read_text(encoding="utf-8")


def test_local_signature_detects_change(tmp_path) -> None:
    target = tmp_path / "report.json"
    target.write_text("a", encoding="utf-8")
    signature = tmp_path / "report.sig.json"
    service = LocalSignatureService(tmp_path / "key.json")
    service.sign_file(target, signature)

    target.write_text("b", encoding="utf-8")

    assert service.verify_file(target, signature) is False


def test_sign_report_cli_outputs_signature(tmp_path) -> None:
    write_isolated_config(tmp_path)
    target = tmp_path / "report.json"
    target.write_text("a", encoding="utf-8")
    signature = tmp_path / "report.sig.json"
    completed = subprocess.run(
        [sys.executable, "-m", "aurora.cli", "--root", str(tmp_path), "sign-report", str(target), str(signature)],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(completed.stdout)

    assert payload["ok"] is True
    assert signature.exists()
