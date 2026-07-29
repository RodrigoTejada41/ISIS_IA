from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass(slots=True)
class ParsedRules:
    raw_text: str
    structured: dict
    warnings: list[str] = field(default_factory=list)
    risk: str = "LOW"
    requires_confirmation: bool = True


class RuleParser:
    def parse(self, text: str) -> ParsedRules:
        clean = " ".join(text.strip().split())
        lower = clean.lower()
        structured = {
            "internet": {},
            "downloads": {},
            "memory": {},
            "domains": {"allowed": [], "blocked": []},
            "limits": {},
        }
        warnings: list[str] = []
        risk = "LOW"

        if re.search(r"\binternet\b|pesquis", lower):
            structured["internet"]["enabled"] = not bool(re.search(r"nao use|sem internet|bloqueie.*internet|offline", lower))
            structured["internet"]["mode"] = "controlled"
        if "modo offline" in lower or "offline total" in lower:
            structured["internet"]["enabled"] = False
            structured["internet"]["mode"] = "blocked"
        if "pesquisa profunda" in lower:
            structured["internet"]["deep_research"] = True
            risk = "MEDIUM"
        if "download" in lower or "baixar" in lower:
            structured["downloads"]["enabled"] = not bool(re.search(r"bloqueie downloads|nao pode baixar|sem download", lower))
            structured["downloads"]["require_confirmation"] = True
            risk = "MEDIUM"
        if re.search(r"execut", lower):
            structured["downloads"]["automatic_execution"] = False
            risk = "HIGH"
        if "cerebro_vivo" in lower or "obsidian" in lower or "memoria" in lower:
            structured["memory"]["require_source"] = True
            structured["memory"]["require_confirmation"] = not bool(re.search(r"salve.*automatic", lower))
        pages = re.search(r"(?:maximo|ate)\s+(\d+)\s+pag", lower)
        if pages:
            structured["limits"]["max_pages_per_research"] = int(pages.group(1))
        minutes = re.search(r"(?:maximo|por)\s+(\d+)\s+min", lower)
        if minutes:
            structured["limits"]["max_duration_minutes"] = int(minutes.group(1))
        for domain in re.findall(r"(?:permita|autorize|libere)\s+(?:acesso ao\s+)?([a-z0-9.-]+\.[a-z]{2,})", lower):
            structured["domains"]["allowed"].append(domain)
        for domain in re.findall(r"(?:bloqueie|proiba)\s+(?:acesso ao\s+)?([a-z0-9.-]+\.[a-z]{2,})", lower):
            structured["domains"]["blocked"].append(domain)
        if not any(structured.values()):
            warnings.append("Regra ambigua: nenhuma acao reconhecida.")
            risk = "MEDIUM"
        if "total" in lower and "sem confirm" in lower:
            warnings.append("Conflito: regras fixas nao podem ser removidas por texto livre.")
            risk = "CRITICAL"
        return ParsedRules(clean, structured, warnings, risk, requires_confirmation=risk in {"MEDIUM", "HIGH", "CRITICAL"})
