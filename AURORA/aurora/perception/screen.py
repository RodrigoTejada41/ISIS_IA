from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class ScreenCaptureMode(str, Enum):
    MANUAL = "MANUAL"
    TEMPORARY = "TEMPORARY"
    CONTROLLED_CONTINUOUS = "CONTROLLED_CONTINUOUS"


@dataclass(slots=True)
class ScreenPrivacyPolicy:
    screen_analysis_enabled: bool = False
    store_images: bool = False
    allowed_modes: set[ScreenCaptureMode] = field(default_factory=lambda: {ScreenCaptureMode.MANUAL})
    blocked_apps: set[str] = field(default_factory=lambda: {"bank", "banco", "password manager", "gerenciador de senhas"})
    sensitive_keywords: set[str] = field(
        default_factory=lambda: {
            "api_key",
            "banco",
            "cartao",
            "cartão",
            "cpf",
            "password",
            "senha",
            "token",
        }
    )

    def allows(self, mode: ScreenCaptureMode, manual_confirmed: bool, app_name: str = "") -> bool:
        if mode not in self.allowed_modes:
            return False
        if mode is ScreenCaptureMode.MANUAL and not manual_confirmed:
            return False
        normalized_app = app_name.lower()
        return not any(blocked in normalized_app for blocked in self.blocked_apps)


@dataclass(slots=True)
class ScreenFrame:
    source: str
    width: int
    height: int
    text: str
    app_name: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass(slots=True)
class ScreenAnalysis:
    source: str
    redacted_text: str
    detected_fields: list[str]
    detected_buttons: list[str]
    detected_errors: list[str]
    detected_menus: list[str]
    privacy_applied: bool
    storage_allowed: bool


class MockScreenProvider:
    def __init__(self, text: str = "Menu Arquivo Editar\nCampo email\nBotao salvar\nErro login invalido") -> None:
        self.text = text

    def capture(self, app_name: str = "mock-app") -> ScreenFrame:
        return ScreenFrame(source="mock", width=1280, height=720, text=self.text, app_name=app_name)


def redact_sensitive_text(text: str, keywords: set[str] | None = None) -> str:
    active_keywords = keywords or ScreenPrivacyPolicy().sensitive_keywords
    redacted = text
    patterns = [
        r"(?i)\b(password|senha|token|api_key)\s*[:=]\s*\S+",
        r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b",
        r"\b(?:\d[ -]*?){13,19}\b",
    ]
    for pattern in patterns:
        redacted = re.sub(pattern, "[REDACTED]", redacted)
    for keyword in active_keywords:
        redacted = re.sub(rf"(?i)\b{re.escape(keyword)}\b\s*[:=]?\s*\S*", "[REDACTED]", redacted)
    return redacted


class ScreenAnalyzer:
    def __init__(self, policy: ScreenPrivacyPolicy | None = None) -> None:
        self.policy = policy or ScreenPrivacyPolicy()

    def analyze(self, frame: ScreenFrame) -> ScreenAnalysis:
        redacted = redact_sensitive_text(frame.text, self.policy.sensitive_keywords)
        lines = [line.strip() for line in redacted.splitlines() if line.strip()]
        return ScreenAnalysis(
            source=frame.source,
            redacted_text=redacted,
            detected_fields=[line for line in lines if self._contains_any(line, {"campo", "input", "field"})],
            detected_buttons=[line for line in lines if self._contains_any(line, {"botao", "botão", "button"})],
            detected_errors=[line for line in lines if self._contains_any(line, {"erro", "error", "falha", "invalid", "invalido"})],
            detected_menus=[line for line in lines if self._contains_any(line, {"menu", "arquivo", "editar"})],
            privacy_applied=redacted != frame.text,
            storage_allowed=self.policy.store_images,
        )

    @staticmethod
    def _contains_any(text: str, terms: set[str]) -> bool:
        normalized = text.lower()
        return any(term in normalized for term in terms)


class ScreenVisionService:
    def __init__(
        self,
        provider: MockScreenProvider,
        analyzer: ScreenAnalyzer | None = None,
        policy: ScreenPrivacyPolicy | None = None,
        mode: ScreenCaptureMode = ScreenCaptureMode.MANUAL,
    ) -> None:
        self.provider = provider
        self.policy = policy or ScreenPrivacyPolicy()
        self.analyzer = analyzer or ScreenAnalyzer(self.policy)
        self.mode = mode

    def capture_and_analyze(self, manual_confirmed: bool, app_name: str = "mock-app") -> ScreenAnalysis:
        if not self.policy.allows(self.mode, manual_confirmed, app_name):
            raise PermissionError("screen capture requires manual confirmation and allowed app")
        return self.analyzer.analyze(self.provider.capture(app_name))
