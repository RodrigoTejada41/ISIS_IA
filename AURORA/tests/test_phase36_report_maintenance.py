from __future__ import annotations

import json
import subprocess
import sys

from aurora.core.report_maintenance import ReportMaintenanceService


def test_report_maintenance_regenerates(tmp_path) -> None:
    result = ReportMaintenanceService(tmp_path).regenerate()

    assert result.ok is True
    assert result.signature_ok is True


def test_reports_regenerate_cli_outputs_json(tmp_path) -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "aurora.cli", "--root", str(tmp_path), "reports-regenerate"],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(completed.stdout)

    assert payload["ok"] is True
    assert payload["signature_ok"] is True
