from __future__ import annotations

import time
from pathlib import Path

from aurora.core.audit import AuditEvent
from aurora.core.commands import CommandResult, CommandRouter
from aurora.core.events import Event, EventBus
from aurora.core.health import HealthMonitor
from aurora.core.memory import RagService
from aurora.core.model_provider import MockModelProvider, ModelPrompt, ModelProviderRegistry, OllamaModelProvider
from aurora.core.runtime import AuroraRuntime
from aurora.core.tools import ToolRegistry, ToolSpec
from aurora.core.permissions import ActionRisk
from aurora.core.security import SecurityGuard
from aurora.voice.factory import build_voice_session


class IsisAssistantCore:
    def __init__(self, root: str | Path) -> None:
        self.runtime = AuroraRuntime(root)
        self.events = EventBus()
        self.tools = ToolRegistry(self.runtime.policy, self.runtime.audit)
        self.health = HealthMonitor(self.runtime.config, self.runtime.resources)
        self.security = SecurityGuard(
            allowed_folders=self.runtime.config.allowed_folders,
            protected_folders=self.runtime.config.protected_folders,
            blocked_commands=self.runtime.config.blocked_commands,
        )
        self.rag = RagService(self.runtime.memory, self.runtime.audit)
        self.model_providers = ModelProviderRegistry([OllamaModelProvider(self.runtime.audit), MockModelProvider()])
        self.commands = CommandRouter(self.runtime.router, self.tools, self.rag, self.runtime.audit, self.events)
        self.started_at: float | None = None
        self.running = False
        self._register_builtin_tools()

    def initialize(self) -> dict:
        self.started_at = time.time()
        self.running = True
        self.events.publish(Event("core.started", {"assistant": self.runtime.config.assistant_name}))
        health = self.health.check()
        self.runtime.audit.record(AuditEvent(action="core.initialize", component="core", params={"health": health}))
        return health

    def handle_text(self, text: str) -> CommandResult:
        if not self.running:
            raise RuntimeError("core is not running")
        return self.commands.handle_text(text)

    def shutdown(self, reason: str = "normal") -> None:
        if not self.running:
            return
        self.running = False
        self.runtime.save_config()
        self.events.publish(Event("core.shutdown", {"reason": reason}))
        self.runtime.audit.record(AuditEvent(action="core.shutdown", component="core", params={"reason": reason}))

    def _register_builtin_tools(self) -> None:
        self.tools.register(
            ToolSpec(
                name="status",
                description="Return ISIS local health and configuration status.",
                permission="system.info",
                risk=ActionRisk.READ_ONLY,
                handler=lambda _: self.health.check(),
            )
        )
        self.tools.register(
            ToolSpec(
                name="security_status",
                description="Return local security guard status.",
                permission="system.info",
                risk=ActionRisk.READ_ONLY,
                handler=lambda _: {
                    "allowed_folders": self.security.allowed_folders,
                    "protected_folders": self.security.protected_folders,
                    "blocked_commands": self.security.blocked_commands,
                },
            )
        )

    def generate_text(self, text: str) -> dict:
        try:
            route = self.handle_text(text)
        except PermissionError as exc:
            return {"command": "blocked", "output": f"Comando bloqueado pela politica local: {exc}"}
        if route.command_type != "model_route" or not route.model:
            return {"command": route.command_type, "output": route.output}
        response = self.model_providers.generate(ModelPrompt(model_id=route.model, prompt=text))
        return {
            "model": response.model_id,
            "provider": response.provider,
            "text": response.text,
            "duration_ms": response.duration_ms,
        }

    def run_voice_once(self, transcript: str = "status", click_to_talk: bool = True) -> dict:
        if not self.running:
            raise RuntimeError("core is not running")
        session = build_voice_session(self.runtime.config, self.runtime.audit, transcript)
        user_text, response_text, audio_path = session.run_once(
            self._voice_response_text,
            click_to_talk=click_to_talk,
        )
        return {
            "transcript": user_text,
            "response": response_text,
            "audio_path": str(audio_path) if audio_path else None,
            "voice_engine": self.runtime.config.voice.tts_engine,
            "stt_engine": self.runtime.config.voice.stt_engine,
        }

    def _voice_response_text(self, text: str) -> str:
        result = self.generate_text(text)
        return str(result.get("text") or result.get("output") or result)
