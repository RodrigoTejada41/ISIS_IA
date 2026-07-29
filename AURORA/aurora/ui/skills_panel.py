from __future__ import annotations

import json
from dataclasses import asdict, dataclass

from aurora.core.permissions import AuthorizationMode
from aurora.core.runtime import AuroraRuntime
from aurora.skills.manager import SandboxResult


@dataclass(slots=True)
class SkillPanelItem:
    name: str
    display_name: str
    version: str
    risk: str
    enabled: bool
    authorization: str
    requires_confirmation: bool


@dataclass(slots=True)
class SkillRunViewResult:
    executed: bool
    reason: str
    result: dict[str, object] | None


class SkillPanelService:
    def __init__(self, runtime: AuroraRuntime) -> None:
        self.runtime = runtime

    def list_skills(self) -> list[SkillPanelItem]:
        items: list[SkillPanelItem] = []
        for path in sorted(self.runtime.skills.skills_dir.iterdir()):
            if not path.is_dir() or not (path / "skill.json").exists():
                continue
            manifest = self.runtime.skills.load_manifest(path)
            authorization = self.runtime.skills.validate_permissions(manifest)
            items.append(
                SkillPanelItem(
                    name=manifest.name,
                    display_name=manifest.display_name,
                    version=manifest.version,
                    risk=manifest.risk_level.value,
                    enabled=manifest.enabled,
                    authorization=authorization.value,
                    requires_confirmation=manifest.requires_confirmation or authorization != AuthorizationMode.AUTO_ALLOW,
                )
            )
        return items

    def run_skill(self, name: str, args_json: str = "{}", approved: bool = False) -> SkillRunViewResult:
        skill_dir = self.runtime.skills.skills_dir / name
        if not skill_dir.exists():
            return SkillRunViewResult(False, "skill not found", None)
        manifest = self.runtime.skills.load_manifest(skill_dir)
        if not manifest.enabled:
            return SkillRunViewResult(False, "skill disabled", None)
        authorization = self.runtime.skills.validate_permissions(manifest)
        if authorization == AuthorizationMode.DENY:
            return SkillRunViewResult(False, "permission denied", None)
        if authorization != AuthorizationMode.AUTO_ALLOW and not approved:
            return SkillRunViewResult(False, "approval required", None)
        try:
            args = json.loads(args_json)
        except json.JSONDecodeError:
            return SkillRunViewResult(False, "invalid json args", None)
        result: SandboxResult = self.runtime.skills.run_in_sandbox(skill_dir, args)
        return SkillRunViewResult(True, "executed in sandbox", asdict(result))


def parse_skill_kv_args(items: list[str] | None) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for item in items or []:
        if "=" not in item:
            raise ValueError("skill args must use key=value")
        key, value = item.split("=", 1)
        if not key:
            raise ValueError("skill arg key cannot be empty")
        parsed[key] = value
    return parsed
