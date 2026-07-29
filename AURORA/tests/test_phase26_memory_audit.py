from __future__ import annotations

import json
import subprocess
import sys

from aurora.core.memory_audit import MemoryAuditLogger
from aurora.core.runtime import AuroraRuntime
from aurora.ui.memory_panel import MemoryPanelService


def test_memory_panel_audits_propose_and_confirm(tmp_path) -> None:
    runtime = AuroraRuntime(tmp_path)
    audit_path = tmp_path / "memory_approvals.jsonl"
    service = MemoryPanelService(runtime, MemoryAuditLogger(audit_path))

    proposed = service.propose("memoria auditada")
    confirmed = service.confirm(proposed.id or "")
    rows = MemoryAuditLogger(audit_path).tail(2)

    assert proposed.ok is True
    assert confirmed.ok is True
    assert [row["action"] for row in rows] == ["memory.propose", "memory.status"]
    assert rows[-1]["status"] == "CONFIRMED"


def test_memory_panel_audits_reject(tmp_path) -> None:
    runtime = AuroraRuntime(tmp_path)
    audit_path = tmp_path / "memory_approvals.jsonl"
    service = MemoryPanelService(runtime, MemoryAuditLogger(audit_path))
    proposed = service.propose("memoria rejeitada")

    rejected = service.reject(proposed.id or "")

    assert rejected.ok is True
    assert MemoryAuditLogger(audit_path).tail(1)[0]["status"] == "REJECTED"


def test_memory_approval_audit_cli_outputs_list(tmp_path) -> None:
    subprocess.run(
        [sys.executable, "-m", "aurora.cli", "--root", str(tmp_path), "ui-memory-propose", "memoria auditavel"],
        check=True,
        capture_output=True,
        text=True,
    )
    completed = subprocess.run(
        [sys.executable, "-m", "aurora.cli", "--root", str(tmp_path), "memory-approval-audit", "--limit", "5"],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(completed.stdout)

    assert isinstance(payload, list)
    assert all("action" in item for item in payload)
