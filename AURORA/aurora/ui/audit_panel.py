from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from aurora.automation.action_audit import UIActionAuditLogger
from aurora.core.key_acl import KeyAclInspector
from aurora.core.memory_audit import MemoryAuditLogger
from aurora.core.privilege_audit import PrivilegeAuditLogger
from aurora.core.report_integrity import ReportIntegrityService
from aurora.core.report_maintenance import ReportMaintenanceService, ReportMaintenanceResult
from aurora.core.runtime import AuroraRuntime


@dataclass(slots=True)
class AuditPanelSnapshot:
    ui_actions: int
    privilege_events: int
    memory_events: int
    report_integrity_ok: bool
    signature_key_restricted: bool
    report_history_count: int
    last_report_generated_at: str | None
    reports_root: str


class AuditPanelService:
    def __init__(self, runtime: AuroraRuntime) -> None:
        self.runtime = runtime
        self.isis_root = Path(runtime.config.paths.isis_root)

    def snapshot(self) -> AuditPanelSnapshot:
        reports_root = self.isis_root / "reports"
        manifest = reports_root / "report_integrity.json"
        report_integrity_ok = ReportIntegrityService(reports_root).verify_manifest(manifest) if manifest.exists() else False
        key_status = KeyAclInspector().inspect(self.isis_root / "config" / "report_signing_key.json")
        history = ReportMaintenanceService(self.isis_root).history(100)
        return AuditPanelSnapshot(
            ui_actions=len(UIActionAuditLogger(self.isis_root / "logs" / "automation" / "ui_actions.jsonl").tail(100)),
            privilege_events=len(PrivilegeAuditLogger(self.isis_root / "logs" / "security" / "privileges.jsonl").tail(100)),
            memory_events=len(MemoryAuditLogger(self.isis_root / "logs" / "security" / "memory_approvals.jsonl").tail(100)),
            report_integrity_ok=report_integrity_ok,
            signature_key_restricted=key_status.restricted,
            report_history_count=len(history),
            last_report_generated_at=str(history[-1]["created_at"]) if history else None,
            reports_root=str(reports_root),
        )

    def regenerate_reports(self) -> ReportMaintenanceResult:
        return ReportMaintenanceService(self.isis_root).regenerate()
