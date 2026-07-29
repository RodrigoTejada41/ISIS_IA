from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Callable

from aurora.core.audit import AuditEvent, AuditLogger
from aurora.core.permissions import ActionRisk, AuthorizationMode, PermissionPolicy


ToolHandler = Callable[[dict[str, Any]], Any]


@dataclass(frozen=True, slots=True)
class ToolSpec:
    name: str
    description: str
    permission: str
    risk: ActionRisk
    handler: ToolHandler
    enabled: bool = True


class ToolRegistry:
    def __init__(self, policy: PermissionPolicy, audit: AuditLogger) -> None:
        self.policy = policy
        self.audit = audit
        self._tools: dict[str, ToolSpec] = {}

    def register(self, spec: ToolSpec) -> None:
        if spec.name in self._tools:
            raise ValueError(f"tool already registered: {spec.name}")
        self._tools[spec.name] = spec

    def list_tools(self) -> list[dict[str, Any]]:
        return [
            {
                "name": spec.name,
                "description": spec.description,
                "permission": spec.permission,
                "risk": spec.risk.value,
                "enabled": spec.enabled,
            }
            for spec in self._tools.values()
        ]

    def execute(self, name: str, params: dict[str, Any] | None = None, confirmed: bool = False) -> Any:
        started = time.time()
        if name not in self._tools:
            raise KeyError(name)
        spec = self._tools[name]
        mode = self.policy.authorize(spec.permission, spec.risk)
        if mode == AuthorizationMode.DENY:
            raise PermissionError(f"tool denied: {name}")
        if mode in {AuthorizationMode.ASK_CONFIRMATION, AuthorizationMode.REQUIRE_STRONG_CONFIRMATION} and not confirmed:
            raise PermissionError(f"tool requires confirmation: {mode.value}")
        result = spec.handler(params or {})
        self.audit.record(
            AuditEvent(
                action=f"tool.{name}",
                component="tools",
                risk=spec.risk.value,
                authorization=mode.value,
                params=params or {},
                started_at=started,
            )
        )
        return result
