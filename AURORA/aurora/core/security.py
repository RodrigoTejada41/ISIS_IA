from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class PermissionState(str, Enum):
    ALLOWED = "ALLOWED"
    DENIED = "DENIED"
    ASK_ALWAYS = "ASK_ALWAYS"
    ALLOWED_ONCE = "ALLOWED_ONCE"
    ALLOWED_SESSION = "ALLOWED_SESSION"
    ALLOWED_PERMANENT = "ALLOWED_PERMANENT"


@dataclass
class SecurityGuard:
    allowed_folders: list[str] = field(default_factory=list)
    protected_folders: list[str] = field(default_factory=list)
    blocked_commands: list[str] = field(default_factory=list)
    permission_states: dict[str, PermissionState] = field(default_factory=dict)

    def validate_path_read(self, path: str | Path) -> bool:
        resolved = Path(path).resolve()
        if any(self._is_relative_to(resolved, Path(item).resolve()) for item in self.protected_folders):
            return False
        if not self.allowed_folders:
            return True
        return any(self._is_relative_to(resolved, Path(item).resolve()) for item in self.allowed_folders)

    def validate_command(self, command: str) -> bool:
        normalized = command.lower().strip()
        return not any(blocked.lower() in normalized for blocked in self.blocked_commands)

    def set_permission_state(self, key: str, state: PermissionState) -> None:
        self.permission_states[key] = state

    def check_permission_state(self, key: str) -> PermissionState:
        return self.permission_states.get(key, PermissionState.ASK_ALWAYS)

    @staticmethod
    def _is_relative_to(path: Path, base: Path) -> bool:
        try:
            path.relative_to(base)
            return True
        except ValueError:
            return False
