from pathlib import Path

from aurora.core.security import PermissionState, SecurityGuard
from aurora.core.assistant import IsisAssistantCore
from aurora.cli import main


def test_security_guard_validates_allowed_and_protected_paths(tmp_path):
    allowed = tmp_path / "allowed"
    protected = allowed / "secret"
    allowed.mkdir()
    protected.mkdir()
    guard = SecurityGuard(allowed_folders=[str(allowed)], protected_folders=[str(protected)])

    assert guard.validate_path_read(allowed / "file.txt") is True
    assert guard.validate_path_read(protected / "token.txt") is False
    assert guard.validate_path_read(tmp_path.parent / "outside.txt") is False


def test_security_guard_blocks_commands():
    guard = SecurityGuard(blocked_commands=["format", "diskpart"])

    assert guard.validate_command("echo ok") is True
    assert guard.validate_command("diskpart /s x") is False


def test_permission_state_defaults_to_ask():
    guard = SecurityGuard()

    assert guard.check_permission_state("files.write") == PermissionState.ASK_ALWAYS
    guard.set_permission_state("files.write", PermissionState.ALLOWED_SESSION)
    assert guard.check_permission_state("files.write") == PermissionState.ALLOWED_SESSION


def test_core_security_status_tool(tmp_path):
    core = IsisAssistantCore(tmp_path)
    core.initialize()

    result = core.tools.execute("security_status", {})

    assert "blocked_commands" in result


def test_cli_security_status(tmp_path, capsys):
    code = main(["--root", str(tmp_path), "security-status"])

    assert code == 0
    assert "blocked_commands" in capsys.readouterr().out
