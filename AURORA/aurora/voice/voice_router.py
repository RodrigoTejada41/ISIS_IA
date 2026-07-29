from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from aurora.core.audit import AuditEvent, AuditLogger
from aurora.voice.tts.base_tts import TTSResult


class VoiceRouter:
    def __init__(self, engines: list[object], audit: AuditLogger) -> None:
        self.engines = engines
        self.audit = audit

    def synthesize(self, text: str, emotion: str = "neutral", speed: float = 1.0, volume: float = 1.0) -> TTSResult | None:
        errors: list[dict[str, str]] = []
        for engine in self.engines:
            name = getattr(engine, "name", "unknown")
            try:
                if not engine.is_available():
                    errors.append({"engine": name, "error": engine.info().error or "unavailable"})
                    continue
                result = engine.synthesize(text, emotion=emotion, speed=speed, volume=volume)
                self.audit.record(AuditEvent(action="voice.tts.synthesize", component="voice", params={"engine": name, "cached": result.cached, "elapsed_ms": result.elapsed_ms}))
                return result
            except Exception as exc:
                errors.append({"engine": name, "error": str(exc)})
                self.audit.record(AuditEvent(action="voice.tts.fallback", component="voice", params={"engine": name, "error": str(exc)}))
        self.audit.record(AuditEvent(action="voice.tts.failed", component="voice", params={"errors": errors}))
        return None

    def status(self) -> list[dict]:
        return [asdict(engine.info()) for engine in self.engines]

