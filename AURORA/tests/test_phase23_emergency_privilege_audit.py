from __future__ import annotations

import json
import subprocess
import sys

from aurora.core.privilege_audit import PrivilegeAuditLogger
from aurora.core.runtime import AuroraRuntime
from aurora.ui.privileges import PrivilegeControlService


def test_emergency_stop_sets_medium_and_audits(tmp_path) -> None:
    runtime = AuroraRuntime(tmp_path)
    audit_path = tmp_path / "logs" / "security" / "privileges.jsonl"
    service = PrivilegeControlService(runtime, audit=PrivilegeAuditLogger(audit_path))

    result = service.emergency_stop()
    rows = PrivilegeAuditLogger(audit_path).tail(1)

    assert result.changed is True
    assert result.profile == "MEDIUM"
    assert rows[0]["action"] == "emergency.stop"


def test_failed_profile_change_is_audited(tmp_path) -> None:
    runtime = AuroraRuntime(tmp_path)
    audit_path = tmp_path / "logs" / "security" / "privileges.jsonl"
    service = PrivilegeControlService(runtime, audit=PrivilegeAuditLogger(audit_path))

    result = service.change_profile("TOTAL", "wrong")
    rows = PrivilegeAuditLogger(audit_path).tail(1)

    assert result.changed is False
    assert rows[0]["success"] is False


def test_emergency_stop_cli_outputs_json() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "aurora.cli", "emergency-stop"],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(completed.stdout)

    assert payload["changed"] is True
    assert payload["profile"] == "MEDIUM"


def test_privilege_audit_cli_outputs_list() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "aurora.cli", "privilege-audit", "--limit", "5"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert isinstance(json.loads(completed.stdout), list)
