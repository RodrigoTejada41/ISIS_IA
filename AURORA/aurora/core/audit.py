from __future__ import annotations

import json
import time
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


SENSITIVE_KEYS = {"password", "senha", "token", "secret", "api_key", "pin"}


def sanitize(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: ("***" if k.lower() in SENSITIVE_KEYS else sanitize(v)) for k, v in value.items()}
    if isinstance(value, list):
        return [sanitize(v) for v in value]
    return value


@dataclass(slots=True)
class AuditEvent:
    action: str
    component: str
    user: str = "local"
    profile: str = "CONTROLLED"
    risk: str = "LOW"
    authorization: str = "AUTO_ALLOW"
    params: dict[str, Any] = field(default_factory=dict)
    result: str = "ok"
    affected_files: list[str] = field(default_factory=list)
    rollback_available: bool = False
    error: str | None = None
    started_at: float = field(default_factory=time.time)
    duration_ms: int = 0
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))


class AuditLogger:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def record(self, event: AuditEvent) -> AuditEvent:
        event.duration_ms = max(0, int((time.time() - event.started_at) * 1000))
        payload = asdict(event)
        payload["params"] = sanitize(payload["params"])
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")
        return event

    def read_all(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        return [json.loads(line) for line in self.path.read_text(encoding="utf-8").splitlines() if line.strip()]
