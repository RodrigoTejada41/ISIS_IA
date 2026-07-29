from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

from aurora.core.audit import AuditEvent, AuditLogger
from aurora.core.events import Event, EventBus
from aurora.core.memory import RagService
from aurora.core.routing import ModelRouter, RouteRequest
from aurora.core.tools import ToolRegistry


@dataclass(frozen=True, slots=True)
class CommandResult:
    command_type: str
    output: Any
    model: str | None = None
    profile: str | None = None
    used_memory_ids: list[str] | None = None


class CommandRouter:
    def __init__(
        self,
        model_router: ModelRouter,
        tools: ToolRegistry,
        rag: RagService,
        audit: AuditLogger,
        events: EventBus,
    ) -> None:
        self.model_router = model_router
        self.tools = tools
        self.rag = rag
        self.audit = audit
        self.events = events

    def handle_text(self, text: str) -> CommandResult:
        started = time.time()
        normalized = text.strip()
        self.events.publish(Event("command.received", {"text": normalized}))
        if normalized.lower() in {"status", "isis status", "estado"}:
            result = CommandResult("status", self.tools.execute("status", {}))
        elif normalized.lower().startswith("memoria:") or normalized.lower().startswith("memória:"):
            query = normalized.split(":", 1)[1].strip()
            context, ids = self.rag.build_context(query)
            result = CommandResult("memory_search", context, used_memory_ids=ids)
        else:
            decision = self.model_router.route(RouteRequest(normalized, needs_memory="memoria" in normalized.lower() or "memória" in normalized.lower()))
            result = CommandResult(
                "model_route",
                {
                    "message": "model selected",
                    "reason": decision.reason,
                    "available": decision.available,
                    "resource_reason": decision.resource_reason,
                },
                model=decision.model.model_id if decision.model else None,
                profile=decision.profile.value,
            )
        self.audit.record(AuditEvent(action="command.handle_text", component="commands", params={"text": normalized, "type": result.command_type}, started_at=started))
        self.events.publish(Event("command.completed", {"type": result.command_type}))
        return result
