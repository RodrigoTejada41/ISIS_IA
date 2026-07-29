from __future__ import annotations

import json
from dataclasses import asdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from aurora.core.audit_report import AuditReportService
from aurora.core.local_signature import LocalSignatureService
from aurora.core.report_integrity import ReportIntegrityService


@dataclass(slots=True)
class ReportMaintenanceResult:
    ok: bool
    audit_report: str
    integrity_manifest: str
    signature: str
    signature_ok: bool


class ReportMaintenanceService:
    def __init__(self, isis_root: str | Path) -> None:
        self.isis_root = Path(isis_root)
        self.reports_root = self.isis_root / "reports"

    def regenerate(self) -> ReportMaintenanceResult:
        audit_report = self.reports_root / "audit_report.json"
        integrity_manifest = self.reports_root / "report_integrity.json"
        signature = self.reports_root / "report_integrity.sig.json"
        AuditReportService(self.isis_root).build(audit_report)
        ReportIntegrityService(self.reports_root).build_manifest(integrity_manifest)
        signer = LocalSignatureService(self.isis_root / "config" / "report_signing_key.json")
        signer.sign_file(integrity_manifest, signature)
        signature_ok = signer.verify_file(integrity_manifest, signature)
        result = ReportMaintenanceResult(True, str(audit_report), str(integrity_manifest), str(signature), signature_ok)
        self._record_history(result)
        return result

    def history(self, limit: int = 20) -> list[dict[str, object]]:
        path = self._history_path()
        if not path.exists():
            return []
        lines = path.read_text(encoding="utf-8").splitlines()[-limit:]
        return [json.loads(line) for line in lines if line.strip()]

    def _record_history(self, result: ReportMaintenanceResult) -> None:
        path = self._history_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"created_at": datetime.now(timezone.utc).isoformat(), **asdict(result)}
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")

    def _history_path(self) -> Path:
        return self.isis_root / "logs" / "security" / "report_maintenance.jsonl"
