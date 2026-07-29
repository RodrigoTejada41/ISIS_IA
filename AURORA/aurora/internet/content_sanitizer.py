from __future__ import annotations

import re
from dataclasses import dataclass, field


SENSITIVE_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_-]{12,}"),
    re.compile(r"(?i)(api[_-]?key|token|senha|password)\s*[:=]\s*\S+"),
    re.compile(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b"),
]

INJECTION_PATTERNS = [
    re.compile(r"(?i)ignore (todas )?(as )?(regras|instrucoes)"),
    re.compile(r"(?i)revele (o )?(prompt|segredo|token|credencial)"),
    re.compile(r"(?i)(execute|rode|apague|delete|envie).{0,40}(comando|arquivo|credencial|senha)"),
]


@dataclass(slots=True)
class SanitizedContent:
    text: str
    suspicious: bool = False
    warnings: list[str] = field(default_factory=list)


class ContentSanitizer:
    def sanitize_query(self, text: str) -> SanitizedContent:
        warnings: list[str] = []
        clean = text
        for pattern in SENSITIVE_PATTERNS:
            if pattern.search(clean):
                warnings.append("dados sensiveis removidos da consulta")
                clean = pattern.sub("[DADO_REMOVIDO]", clean)
        return SanitizedContent(clean, bool(warnings), warnings)

    def sanitize_external_text(self, text: str) -> SanitizedContent:
        warnings: list[str] = []
        suspicious = False
        for pattern in INJECTION_PATTERNS:
            if pattern.search(text):
                suspicious = True
                warnings.append("possivel prompt injection detectado")
                break
        compact = re.sub(r"\s+", " ", text).strip()
        return SanitizedContent(compact[:12000], suspicious, warnings)
