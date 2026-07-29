from __future__ import annotations

import json
import subprocess
import sys

from aurora.core.report_integrity import ReportIntegrityService


def test_report_integrity_manifest_and_verify(tmp_path) -> None:
    reports = tmp_path / "reports"
    reports.mkdir()
    (reports / "a.json").write_text('{"ok":true}', encoding="utf-8")
    (reports / "a.sig.json").write_text('{"signature":"old"}', encoding="utf-8")
    manifest_path = reports / "manifest.json"

    manifest = ReportIntegrityService(reports).build_manifest(manifest_path)

    assert len(manifest.reports) == 1
    assert ReportIntegrityService(reports).verify_manifest(manifest_path) is True


def test_report_integrity_detects_change(tmp_path) -> None:
    reports = tmp_path / "reports"
    reports.mkdir()
    target = reports / "a.json"
    target.write_text("a", encoding="utf-8")
    manifest_path = reports / "manifest.json"
    service = ReportIntegrityService(reports)
    service.build_manifest(manifest_path)

    target.write_text("b", encoding="utf-8")

    assert service.verify_manifest(manifest_path) is False


def test_report_integrity_cli_outputs_manifest(tmp_path) -> None:
    output = tmp_path / "manifest.json"
    completed = subprocess.run(
        [sys.executable, "-m", "aurora.cli", "--root", str(tmp_path), "report-integrity", str(output)],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(completed.stdout)

    assert isinstance(payload["reports"], list)
    assert output.exists()
