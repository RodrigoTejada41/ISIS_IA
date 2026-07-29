from __future__ import annotations

import json
import subprocess
import sys

from aurora.core.report_maintenance import ReportMaintenanceService


def test_report_maintenance_history(tmp_path) -> None:
    service = ReportMaintenanceService(tmp_path)

    service.regenerate()
    rows = service.history()

    assert len(rows) == 1
    assert rows[0]["signature_ok"] is True


def test_reports_history_cli_outputs_json(tmp_path) -> None:
    subprocess.run(
        [sys.executable, "-m", "aurora.cli", "--root", str(tmp_path), "reports-regenerate"],
        check=True,
        capture_output=True,
        text=True,
    )
    completed = subprocess.run(
        [sys.executable, "-m", "aurora.cli", "--root", str(tmp_path), "reports-history"],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(completed.stdout)

    assert isinstance(payload, list)
    assert payload[-1]["signature_ok"] is True
