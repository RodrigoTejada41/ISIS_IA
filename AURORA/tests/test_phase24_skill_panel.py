from __future__ import annotations

import json
import subprocess
import sys

from aurora.core.runtime import AuroraRuntime
from aurora.ui.skills_panel import SkillPanelService, parse_skill_kv_args


def test_skill_panel_lists_initial_skills(tmp_path) -> None:
    runtime = AuroraRuntime("D:/ISIS_IA/AURORA")
    items = SkillPanelService(runtime).list_skills()

    assert len(items) >= 10
    assert any(item.name == "system_info" for item in items)


def test_skill_panel_requires_approval_when_policy_requires(tmp_path) -> None:
    runtime = AuroraRuntime("D:/ISIS_IA/AURORA")
    result = SkillPanelService(runtime).run_skill("system_info", "{}", approved=False)

    if result.executed:
        assert result.reason == "executed in sandbox"
    else:
        assert result.reason in {"approval required", "permission denied"}


def test_skill_panel_runs_approved_skill() -> None:
    runtime = AuroraRuntime("D:/ISIS_IA/AURORA")
    result = SkillPanelService(runtime).run_skill("project_list", '{"root":"D:/ISIS_IA"}', approved=True)

    assert result.executed is True
    assert result.result is not None
    assert result.result["exit_code"] == 0


def test_ui_skills_snapshot_cli_outputs_json() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "aurora.cli", "ui-skills-snapshot"],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(completed.stdout)

    assert isinstance(payload, list)
    assert any(item["name"] == "system_info" for item in payload)


def test_parse_skill_kv_args() -> None:
    assert parse_skill_kv_args(["root=D:/ISIS_IA"]) == {"root": "D:/ISIS_IA"}
