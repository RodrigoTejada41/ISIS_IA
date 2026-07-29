from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from aurora.core.memory_audit import MemoryAuditLogger, MemoryAuditRecord
from aurora.core.memory import MemoryRecord, MemoryStatus, MemoryType
from aurora.core.runtime import AuroraRuntime


@dataclass(slots=True)
class MemoryPanelItem:
    id: str
    type: str
    status: str
    sensitivity: str
    project: str | None
    content_preview: str


@dataclass(slots=True)
class MemoryPanelResult:
    ok: bool
    reason: str
    id: str | None = None


class MemoryPanelService:
    def __init__(self, runtime: AuroraRuntime, audit: MemoryAuditLogger | None = None) -> None:
        self.runtime = runtime
        self.audit = audit or MemoryAuditLogger(f"{runtime.config.paths.isis_root}/logs/security/memory_approvals.jsonl")

    def list_records(self, status: str | None = None, limit: int = 20) -> list[MemoryPanelItem]:
        memory_status = MemoryStatus(status) if status else None
        rows = self.runtime.memory.list_by_status(memory_status, limit)
        return [
            MemoryPanelItem(
                id=row["id"],
                type=row["type"],
                status=row["status"],
                sensitivity=row["sensitivity"],
                project=row["project"],
                content_preview=str(row["content"])[:240],
            )
            for row in rows
        ]

    def export_report(self, output_path: str | Path, status: str | None = None, limit: int = 100, fmt: str = "json") -> MemoryPanelResult:
        records = self.list_records(status, limit)
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        if fmt == "json":
            payload = {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "status": status,
                "count": len(records),
                "records": [asdict(item) for item in records],
            }
            path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        elif fmt == "md":
            lines = [
                "# Memory Report",
                "",
                f"- Generated at: {datetime.now(timezone.utc).isoformat()}",
                f"- Status filter: {status or 'ALL'}",
                f"- Count: {len(records)}",
                "",
            ]
            for item in records:
                lines.extend([f"## {item.id}", "", f"- Type: {item.type}", f"- Status: {item.status}", f"- Sensitivity: {item.sensitivity}", "", item.content_preview, ""])
            path.write_text("\n".join(lines), encoding="utf-8")
        else:
            return MemoryPanelResult(False, "invalid export format")
        self._record("memory.export", str(path), status or "ALL", True, f"exported {len(records)} records")
        return MemoryPanelResult(True, "memory report exported", str(path))

    def propose(self, content: str, memory_type: str = MemoryType.PROJECT_KNOWLEDGE.value, project: str | None = None, tags: str = "") -> MemoryPanelResult:
        if not content.strip():
            self._record("memory.propose", "", MemoryStatus.PROPOSED.value, False, "content required")
            return MemoryPanelResult(False, "content required")
        record_id = self.runtime.memory.add(
            MemoryRecord(
                content=content.strip(),
                type=MemoryType(memory_type),
                origin="ui",
                user="local",
                project=project,
                tags=tags,
                status=MemoryStatus.PROPOSED,
            )
        )
        self._record("memory.propose", record_id, MemoryStatus.PROPOSED.value, True, "memory proposed")
        return MemoryPanelResult(True, "memory proposed", record_id)

    def set_status(self, record_id: str, status: str) -> MemoryPanelResult:
        if not record_id:
            self._record("memory.status", "", status, False, "id required")
            return MemoryPanelResult(False, "id required")
        memory_status = MemoryStatus(status)
        self.runtime.memory.set_status(record_id, memory_status)
        self._record("memory.status", record_id, memory_status.value, True, f"memory {memory_status.value.lower()}")
        return MemoryPanelResult(True, f"memory {memory_status.value.lower()}", record_id)

    def confirm(self, record_id: str) -> MemoryPanelResult:
        return self.set_status(record_id, MemoryStatus.CONFIRMED.value)

    def reject(self, record_id: str) -> MemoryPanelResult:
        return self.set_status(record_id, MemoryStatus.REJECTED.value)

    def _record(self, action: str, memory_id: str, status: str, success: bool, reason: str) -> None:
        self.audit.record(MemoryAuditRecord(action, memory_id, status, success, reason))
