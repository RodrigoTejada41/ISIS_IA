from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from enum import Enum

from .audit import AuditEvent, AuditLogger
from .resources import ResourceLimits, ResourceMonitor


class ModelProfile(str, Enum):
    GENERAL = "GENERAL"
    FAST = "FAST"
    REASONING = "REASONING"
    CODING = "CODING"
    VISION = "VISION"
    EMBEDDING = "EMBEDDING"
    SUMMARIZATION = "SUMMARIZATION"
    CLASSIFICATION = "CLASSIFICATION"


@dataclass(frozen=True, slots=True)
class ModelSpec:
    model_id: str
    profiles: set[ModelProfile]
    estimated_memory_mb: int
    context_tokens: int = 4096
    enabled: bool = True
    priority: int = 100


@dataclass(frozen=True, slots=True)
class RouteRequest:
    prompt: str
    has_image: bool = False
    context_tokens: int = 0
    preferred_profile: ModelProfile | None = None
    manual_model_id: str | None = None
    needs_memory: bool = False


@dataclass(frozen=True, slots=True)
class RouteDecision:
    profile: ModelProfile
    model: ModelSpec | None
    reason: str
    fallback_used: bool
    available: bool
    latency_estimate_ms: int
    resource_reason: str


class ModelRouter:
    def __init__(
        self,
        models: list[ModelSpec],
        resource_monitor: ResourceMonitor,
        audit: AuditLogger,
        limits: ResourceLimits | None = None,
    ) -> None:
        self.models = models
        self.resource_monitor = resource_monitor
        self.audit = audit
        self.limits = limits or ResourceLimits()

    def route(self, request: RouteRequest) -> RouteDecision:
        started = time.time()
        profile, reason = self._select_profile(request)
        ordered_profiles = [profile, ModelProfile.GENERAL]
        fallback_used = False

        if request.manual_model_id:
            model = next((m for m in self.models if m.model_id == request.manual_model_id and m.enabled), None)
            if model:
                ok, resource_reason = self.resource_monitor.can_load(model.estimated_memory_mb, request.context_tokens // 2, self.limits)
                decision = RouteDecision(profile, model, "manual model selected", False, ok, 50, resource_reason)
                self._audit(request, decision, started)
                return decision

        for wanted in ordered_profiles:
            candidates = sorted(
                [m for m in self.models if m.enabled and wanted in m.profiles],
                key=lambda m: (m.priority, m.estimated_memory_mb),
            )
            for model in candidates:
                ok, resource_reason = self.resource_monitor.can_load(model.estimated_memory_mb, request.context_tokens // 2, self.limits)
                if ok:
                    decision = RouteDecision(wanted, model, reason, fallback_used or wanted != profile, True, 100, resource_reason)
                    self._audit(request, decision, started)
                    return decision
            fallback_used = True

        decision = RouteDecision(profile, None, reason, fallback_used, False, 0, "no available model")
        self._audit(request, decision, started)
        return decision

    def _select_profile(self, request: RouteRequest) -> tuple[ModelProfile, str]:
        text = request.prompt.lower()
        if request.preferred_profile:
            return request.preferred_profile, "user preferred profile"
        if request.has_image:
            return ModelProfile.VISION, "image input"
        if request.needs_memory or "memoria" in text or "memória" in text:
            return ModelProfile.EMBEDDING, "memory lookup requested"
        if "resuma" in text or "resumo" in text or "summarize" in text:
            return ModelProfile.SUMMARIZATION, "summary intent"
        if re.search(r"\bc[oó]digos?\b", text) or re.search(r"```|def |class |function |select \\* from", request.prompt, re.I):
            return ModelProfile.CODING, "code intent"
        if len(request.prompt) > 1200 or request.context_tokens > 6000:
            return ModelProfile.REASONING, "long or complex context"
        if len(request.prompt) < 160:
            return ModelProfile.FAST, "short simple prompt"
        return ModelProfile.GENERAL, "general prompt"

    def _audit(self, request: RouteRequest, decision: RouteDecision, started: float) -> None:
        self.audit.record(
            AuditEvent(
                action="model.route",
                component="router",
                params={
                    "task": request.prompt[:200],
                    "profile": decision.profile.value,
                    "model": decision.model.model_id if decision.model else None,
                    "reason": decision.reason,
                    "availability": decision.available,
                    "fallback": decision.fallback_used,
                    "resource_reason": decision.resource_reason,
                },
                started_at=started,
            )
        )
