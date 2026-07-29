from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass(slots=True)
class KeyAclStatus:
    path: str
    exists: bool
    inspector_available: bool
    inherited: bool
    everyone_present: bool
    authenticated_users_modify: bool
    restricted: bool
    raw: str


@dataclass(slots=True)
class KeyAclApplyResult:
    applied: bool
    path: str
    backup_path: str | None
    commands: list[list[str]]
    success: bool
    message: str


class KeyAclInspector:
    def inspect(self, path: str | Path) -> KeyAclStatus:
        target = Path(path)
        if not target.exists():
            return KeyAclStatus(str(target), False, shutil.which("icacls") is not None, False, False, False, False, "")
        if not shutil.which("icacls"):
            return KeyAclStatus(str(target), True, False, False, False, False, False, "")
        proc = subprocess.run(["icacls", str(target)], capture_output=True, text=True, timeout=5)
        raw = proc.stdout
        normalized = raw.lower()
        everyone_present = "everyone:" in normalized or "todos:" in normalized
        authenticated_users_modify = (
            "authenticated users:" in normalized
            or "usuários autenticados:" in normalized
            or "usu\xa0rios autenticados:" in normalized
        ) and "(m)" in normalized
        inherited = "(i)" in normalized
        restricted = proc.returncode == 0 and not everyone_present and not authenticated_users_modify
        return KeyAclStatus(str(target), True, True, inherited, everyone_present, authenticated_users_modify, restricted, raw.strip())


class KeyAclManager:
    def __init__(self, inspector: KeyAclInspector | None = None) -> None:
        self.inspector = inspector or KeyAclInspector()

    def apply_restricted(self, path: str | Path, apply: bool = False) -> KeyAclApplyResult:
        target = Path(path)
        backup_path = target.with_name(f"{target.stem}_acl_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.txt")
        user = self._current_user()
        commands = [
            ["icacls", str(target), "/save", str(backup_path)],
            ["icacls", str(target), "/inheritance:r"],
            ["icacls", str(target), "/grant:r", f"{user}:F"],
            ["icacls", str(target), "/grant:r", "*S-1-5-18:F"],
            ["icacls", str(target), "/grant:r", "*S-1-5-32-544:F"],
        ]
        if not apply:
            return KeyAclApplyResult(False, str(target), str(backup_path), commands, True, "dry run")
        if not target.exists():
            return KeyAclApplyResult(False, str(target), None, commands, False, "key file not found")
        if not shutil.which("icacls"):
            return KeyAclApplyResult(False, str(target), None, commands, False, "icacls not available")
        for command in commands:
            proc = subprocess.run(command, capture_output=True, text=True, timeout=10)
            if proc.returncode != 0:
                return KeyAclApplyResult(True, str(target), str(backup_path), commands, False, proc.stderr.strip() or proc.stdout.strip())
        status = self.inspector.inspect(target)
        return KeyAclApplyResult(True, str(target), str(backup_path), commands, status.restricted, "restricted" if status.restricted else "applied but not restricted")

    def rollback(self, path: str | Path, backup_path: str | Path, apply: bool = False) -> KeyAclApplyResult:
        target = Path(path)
        backup = Path(backup_path)
        command = ["icacls", str(target.parent), "/restore", str(backup)]
        if not apply:
            return KeyAclApplyResult(False, str(target), str(backup), [command], True, "dry run")
        if not backup.exists():
            return KeyAclApplyResult(False, str(target), str(backup), [command], False, "backup not found")
        proc = subprocess.run(command, capture_output=True, text=True, timeout=10)
        return KeyAclApplyResult(True, str(target), str(backup), [command], proc.returncode == 0, proc.stderr.strip() or proc.stdout.strip())

    @staticmethod
    def _current_user() -> str:
        domain = os.environ.get("USERDOMAIN", "")
        user = os.environ.get("USERNAME") or os.getlogin()
        return f"{domain}\\{user}" if domain else user
