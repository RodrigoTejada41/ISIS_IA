import json

import pytest

from aurora.core.audit import AuditLogger
from aurora.core.permissions import AuthorizationMode, PermissionPolicy, PrivilegeProfile
from aurora.skills.manager import SkillManager


def create_skill(path, version="1.0.0", code="print('ok')"):
    path.mkdir(parents=True, exist_ok=True)
    (path / "skill.json").write_text(
        json.dumps(
            {
                "id": "system_info",
                "name": "system_info",
                "display_name": "System Info",
                "description": "Read basic computer information",
                "version": version,
                "author": "Aurora",
                "entrypoint": "main.py",
                "permissions": ["system.info"],
                "risk_level": "READ_ONLY",
                "requires_confirmation": False,
                "timeout_seconds": 2,
                "enabled": True,
                "checksum": "",
            }
        ),
        encoding="utf-8",
    )
    (path / "main.py").write_text(code, encoding="utf-8")


def test_manifest_permission_validation(tmp_path):
    staged = tmp_path / "staged"
    create_skill(staged)
    manager = SkillManager(tmp_path / "skills", PermissionPolicy(PrivilegeProfile.CONTROLLED), AuditLogger(tmp_path / "audit.jsonl"))

    manifest = manager.load_manifest(staged)

    assert manager.validate_permissions(manifest) == AuthorizationMode.AUTO_ALLOW


def test_sandbox_execution(tmp_path):
    staged = tmp_path / "staged"
    create_skill(staged, code="import sys; print('sandbox ok')")
    manager = SkillManager(tmp_path / "skills", PermissionPolicy(), AuditLogger(tmp_path / "audit.jsonl"))

    result = manager.run_in_sandbox(staged)

    assert result.exit_code == 0
    assert "sandbox ok" in result.stdout


def test_install_requires_approval(tmp_path):
    staged = tmp_path / "staged"
    create_skill(staged)
    manager = SkillManager(tmp_path / "skills", PermissionPolicy(), AuditLogger(tmp_path / "audit.jsonl"))

    with pytest.raises(PermissionError):
        manager.install_after_approval(staged, approved=False, reason="test")


def test_install_and_rollback(tmp_path):
    staged = tmp_path / "staged"
    create_skill(staged, "1.0.0", "print('v1')")
    manager = SkillManager(tmp_path / "skills", PermissionPolicy(), AuditLogger(tmp_path / "audit.jsonl"))
    target = manager.install_after_approval(staged, approved=True, reason="test")

    (target / "main.py").write_text("print('changed')", encoding="utf-8")
    manager.rollback("system_info", "1.0.0")

    assert "v1" in (target / "main.py").read_text(encoding="utf-8")


def test_all_initial_skill_manifests_are_valid(tmp_path):
    manager = SkillManager("data/skills", PermissionPolicy(), AuditLogger(tmp_path / "audit.jsonl"))

    manifests = [manager.load_manifest(path) for path in manager.skills_dir.iterdir() if path.is_dir()]

    assert len(manifests) >= 10
    assert {m.name for m in manifests} >= {"system_info", "file_search", "note_search"}
