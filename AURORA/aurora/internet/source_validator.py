from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass(slots=True)
class SourceScore:
    url: str
    domain: str
    level: str
    score: int
    reasons: list[str]


class SourceValidator:
    def __init__(self, trusted_domains: list[str]) -> None:
        self.trusted = set(trusted_domains)

    def score(self, url: str, has_date: bool = False, has_author: bool = False) -> SourceScore:
        domain = (urlparse(url).hostname or "").lower()
        score = 30
        reasons: list[str] = []
        if any(domain == item or domain.endswith("." + item) for item in self.trusted):
            score += 35
            reasons.append("dominio confiavel")
        if domain.endswith(".gov") or ".gov." in domain:
            score += 25
            reasons.append("fonte governamental")
        if domain.endswith(".edu") or ".edu." in domain:
            score += 20
            reasons.append("fonte academica")
        if has_date:
            score += 10
            reasons.append("data identificada")
        if has_author:
            score += 5
            reasons.append("autor identificado")
        level = "Alta confiabilidade" if score >= 70 else "Confiabilidade moderada" if score >= 45 else "Nao verificada"
        return SourceScore(url, domain, level, min(score, 100), reasons)
