from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from aurora.automation.action_audit import UIActionAuditLogger
from aurora.core.memory_audit import MemoryAuditLogger
from aurora.core.privilege_audit import PrivilegeAuditLogger


@dataclass(slots=True)
class AuditReportResult:
    ok: bool
    path: str
    ui_actions: int
    privilege_events: int
    memory_events: int


class AuditReportService:
    def __init__(self, isis_root: str | Path) -> None:
        self.isis_root = Path(isis_root)

    def build(self, output_path: str | Path, limit: int = 100, fmt: str = "json") -> AuditReportResult:
        ui_actions = UIActionAuditLogger(self.isis_root / "logs" / "automation" / "ui_actions.jsonl").tail(limit)
        privilege_events = PrivilegeAuditLogger(self.isis_root / "logs" / "security" / "privileges.jsonl").tail(limit)
        memory_events = MemoryAuditLogger(self.isis_root / "logs" / "security" / "memory_approvals.jsonl").tail(limit)
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        if fmt == "json":
            path.write_text(
                json.dumps(
                    {
                        "generated_at": datetime.now(timezone.utc).isoformat(),
                        "ui_actions": ui_actions,
                        "privilege_events": privilege_events,
                        "memory_events": memory_events,
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
        elif fmt == "md":
            lines = [
                "# Audit Report",
                "",
                f"- Generated at: {datetime.now(timezone.utc).isoformat()}",
                f"- UI actions: {len(ui_actions)}",
                f"- Privilege events: {len(privilege_events)}",
                f"- Memory events: {len(memory_events)}",
                "",
                "## UI Actions",
                "",
                *[f"- {item}" for item in ui_actions],
                "",
                "## Privileges",
                "",
                *[f"- {item}" for item in privilege_events],
                "",
                "## Memory",
                "",
                *[f"- {item}" for item in memory_events],
            ]
            path.write_text("\n".join(lines), encoding="utf-8")
        else:
            raise ValueError("invalid format")
        return AuditReportResult(True, str(path), len(ui_actions), len(privilege_events), len(memory_events))
