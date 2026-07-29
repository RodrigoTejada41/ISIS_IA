from __future__ import annotations

from pathlib import Path

from aurora.core.audit import AuditLogger
from aurora.core.config import AuroraConfig, ConfigStore
from aurora.core.memory import MemoryStore
from aurora.core.permissions import PermissionPolicy
from aurora.core.resources import ResourceMonitor
from aurora.core.routing import ModelRouter, ModelSpec
from aurora.skills.manager import SkillManager


class AuroraRuntime:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.config_store = ConfigStore(self.root / "data" / "config.json")
        self.config: AuroraConfig = self.config_store.load()
        self.audit = AuditLogger(self.root / "data" / "audit" / "audit.jsonl")
        self.policy = PermissionPolicy(profile=self.config.profile)
        self.memory = MemoryStore(self.root / "data" / "memory" / "memory.sqlite", self.audit)
        self.resources = ResourceMonitor()
        self.skills = SkillManager(self.root / "data" / "skills", self.policy, self.audit)
        self.router = ModelRouter(self._models(), self.resources, self.audit, self.config.resource_limits)

    def save_config(self) -> None:
        self.config.profile = self.policy.profile
        self.config_store.save(self.config)

    def _models(self) -> list[ModelSpec]:
        return [
            ModelSpec(
                model_id=item.model_id,
                profiles=set(item.profiles),
                estimated_memory_mb=item.estimated_memory_mb,
                context_tokens=item.context_tokens,
                enabled=item.enabled,
                priority=item.priority,
            )
            for item in self.config.models
        ]
