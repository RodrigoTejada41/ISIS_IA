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


def test_signature_key_status_without_key(tmp_path) -> None:
    status = LocalSignatureService(tmp_path / "key.json").status()

    assert status.configured is False
    assert status.backup_count == 0


def test_signature_key_rotation_creates_backup(tmp_path) -> None:
    service = LocalSignatureService(tmp_path / "key.json")
    first = service.ensure_key()

    result = service.rotate_key()
    status = service.status()

    assert result.rotated is True
    assert result.old_key_id == first
    assert result.new_key_id != first
    assert result.backup_path is not None
    assert status.backup_count == 1


def test_signature_key_status_cli_outputs_json(tmp_path) -> None:
    write_isolated_config(tmp_path)
    completed = subprocess.run(
        [sys.executable, "-m", "aurora.cli", "--root", str(tmp_path), "signature-key-status"],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(completed.stdout)

    assert "configured" in payload
    assert "backup_count" in payload


def test_signature_key_rotate_cli_outputs_json(tmp_path) -> None:
    write_isolated_config(tmp_path)
    subprocess.run(
        [sys.executable, "-m", "aurora.cli", "--root", str(tmp_path), "sign-report", __file__, str(tmp_path / "sig.json")],
        check=True,
        capture_output=True,
        text=True,
    )
    completed = subprocess.run(
        [sys.executable, "-m", "aurora.cli", "--root", str(tmp_path), "signature-key-rotate"],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(completed.stdout)

    assert payload["rotated"] is True
    assert payload["backup_path"]
