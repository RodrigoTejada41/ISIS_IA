from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from aurora.automation.ui import UIActionResult


@dataclass(slots=True)
class UIActionAuditRecord:
    status: str
    action_type: str
    target: str
    reason: str
    approved: bool
    real_execution: bool
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass(slots=True)
class PermissionPanelSnapshot:
    real_ui_execution_enabled: bool
    approval_per_action: bool
    screen_real_capture_enabled: bool
    screen_storage_enabled: bool
    blocked_targets: list[str]


class UIActionAuditLogger:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def record(self, result: UIActionResult, approved: bool, real_execution: bool) -> UIActionAuditRecord:
        record = UIActionAuditRecord(
            status=result.status.value,
            action_type=result.action.action_type.value,
            target=result.action.target,
            reason=result.reason,
            approved=approved,
            real_execution=real_execution,
        )
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(asdict(record), ensure_ascii=False) + "\n")
        return record

    def tail(self, limit: int = 20) -> list[dict[str, object]]:
        if not self.path.exists():
            return []
        lines = self.path.read_text(encoding="utf-8").splitlines()[-limit:]
        return [json.loads(line) for line in lines if line.strip()]
