from __future__ import annotations

from aurora.core.report_maintenance import ReportMaintenanceService
from aurora.core.runtime import AuroraRuntime
from aurora.ui.audit_panel import AuditPanelService


def test_audit_panel_includes_report_history(tmp_path) -> None:
    runtime = AuroraRuntime(tmp_path)
    ReportMaintenanceService(runtime.config.paths.isis_root).regenerate()

    snapshot = AuditPanelService(runtime).snapshot()

    assert snapshot.report_history_count >= 1
    assert snapshot.last_report_generated_at is not None
