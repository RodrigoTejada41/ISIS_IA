from __future__ import annotations

import json
import subprocess
import sys

from aurora.core.audit_report import AuditReportService
from aurora.core.memory_audit import MemoryAuditLogger, MemoryAuditRecord
from aurora.core.privilege_audit import PrivilegeAuditLogger, PrivilegeAuditRecord


def test_audit_report_json(tmp_path) -> None:
    MemoryAuditLogger(tmp_path / "logs/security/memory_approvals.jsonl").record(MemoryAuditRecord("memory.propose", "1", "PROPOSED", True, "ok"))
    PrivilegeAuditLogger(tmp_path / "logs/security/privileges.jsonl").record(PrivilegeAuditRecord("emergency.stop", "CONTROLLED", "MEDIUM", True, "ok"))
    output = tmp_path / "audit.json"

    result = AuditReportService(tmp_path).build(output)
    payload = json.loads(output.read_text(encoding="utf-8"))

    assert result.ok is True
    assert result.memory_events == 1
    assert result.privilege_events == 1
    assert "memory_events" in payload


def test_audit_report_markdown(tmp_path) -> None:
    output = tmp_path / "audit.md"

    result = AuditReportService(tmp_path).build(output, fmt="md")

    assert result.ok is True
    assert "Audit Report" in output.read_text(encoding="utf-8")


def test_audit_report_cli_outputs_file(tmp_path) -> None:
    output = tmp_path / "audit.json"
    completed = subprocess.run(
        [sys.executable, "-m", "aurora.cli", "--root", str(tmp_path), "audit-report", str(output)],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(completed.stdout)

    assert payload["ok"] is True
    assert output.exists()
