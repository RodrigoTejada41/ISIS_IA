from __future__ import annotations

import time
import uuid
from dataclasses import asdict
from pathlib import Path

from aurora.internet.content_sanitizer import ContentSanitizer
from aurora.internet.domain_policy import DomainPolicy
from aurora.internet.page_reader import PageReader
from aurora.internet.rate_limiter import RateLimiter
from aurora.internet.research_cache import ResearchCache
from aurora.internet.research_history import ResearchHistory
from aurora.internet.search_provider import CascadingSearchProvider
from aurora.internet.source_validator import SourceValidator
from aurora.permissions.permission_engine import ActionContext, PermissionEngine


class ResearchAgent:
    def __init__(self, config, storage_root: Path) -> None:
        self.config = config
        self.settings = config.internet
        self.storage_root = storage_root
        self.permissions = PermissionEngine(config, storage_root / "config" / "permissions")
        self.cache = ResearchCache(storage_root / "data" / "cache" / "research")
        self.history = ResearchHistory(storage_root / "data" / "databases" / "research_history.sqlite")
        self.sanitizer = ContentSanitizer()
        self.domain_policy = DomainPolicy(self.settings.allowed_domains, self.settings.trusted_domains, self.settings.blocked_domains, self.settings.allow_private_networks)
        self.source_validator = SourceValidator(self.settings.trusted_domains)
        self.provider = CascadingSearchProvider(timeout_seconds=self.settings.timeout_seconds)
        self.reader = PageReader(timeout_seconds=self.settings.timeout_seconds, max_bytes=self.settings.max_page_bytes, url_validator=self.domain_policy.validate_url)
        self.rate_limiter = RateLimiter(self.settings.requests_per_minute, self.settings.requests_per_hour)

    def should_search(self, prompt: str) -> bool:
        lower = prompt.lower()
        explicit = ["pesquise", "procure", "internet", "verifique", "fontes", "noticia", "preco", "clima", "versao", "documentacao atual", "hoje", "atualizado"]
        return any(item in lower for item in explicit)

    def research(self, query: str, mode: str = "quick", confirmed: bool = False, project: str = "") -> dict:
        started = time.time()
        sanitized = self.sanitizer.sanitize_query(query)
        decision = self.permissions.evaluate(ActionContext("internet.search", sanitized.text, project=project, confirmed=confirmed, risk="LOW"))
        if decision.status == "confirm":
            return {"ok": False, "status": "needs_confirmation", "decision": asdict(decision), "query": sanitized.text}
        if decision.is_denied:
            return {"ok": False, "status": "blocked", "decision": asdict(decision), "query": sanitized.text}
        if not self.rate_limiter.allow():
            return {"ok": False, "status": "rate_limited", "error": "Limite de pesquisa atingido."}

        max_results = min(self.settings.max_results if mode == "quick" else self.settings.deep_max_results, self.settings.max_results_hard_limit)
        max_pages = min(self.settings.max_pages if mode == "quick" else self.settings.deep_max_pages, self.settings.max_pages_hard_limit)
        cache_key = self.cache.key(sanitized.text, mode, self.provider.name)
        if self.settings.use_cache:
            cached = self.cache.get(cache_key, self.settings.cache_ttl_seconds)
            if cached:
                cached["cached"] = True
                return cached

        results = self.provider.search(sanitized.text, max_results=max_results)
        sources: list[dict] = []
        pages_read = 0
        for result in results:
            url_decision = self.domain_policy.validate_url(result.url)
            if not url_decision.allowed:
                sources.append({**asdict(result), "blocked": True, "block_reason": url_decision.reason})
                continue
            score = self.source_validator.score(result.url)
            source = {**asdict(result), "domain": url_decision.domain, "score": asdict(score), "blocked": False}
            if pages_read < max_pages:
                try:
                    page = self.reader.read(result.url)
                    source["page"] = {"title": page.title, "excerpt": page.text[:900], "hash": page.content_hash, "suspicious": page.suspicious, "warnings": page.warnings or []}
                    pages_read += 1
                except Exception as exc:
                    source["read_error"] = str(exc)
            sources.append(source)

        usable = [item for item in sources if not item.get("blocked")]
        best_score = max([(item.get("score") or {}).get("score", 0) for item in usable] or [0])
        confidence = "Alta" if best_score >= 70 else "Moderada" if best_score >= 55 or len(usable) >= 2 else "Baixa"
        summary = self._summary(sanitized.text, usable, confidence)
        payload = {
            "ok": True,
            "id": str(uuid.uuid4()),
            "query": sanitized.text,
            "mode": mode,
            "provider": self.provider.name,
            "cached": False,
            "summary": summary,
            "confidence": confidence,
            "sources": sources,
            "consulted_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "duration_ms": int((time.time() - started) * 1000),
            "warnings": sanitized.warnings,
        }
        if self.settings.use_cache:
            self.cache.put(cache_key, payload)
        self.history.add(payload["id"], sanitized.text, mode, "ok", sources, summary, {"confidence": confidence})
        return payload

    def _summary(self, query: str, sources: list[dict], confidence: str) -> str:
        if not sources:
            return f"Nao encontrei fonte publica permitida para: {query}"
        lines = [f"Pesquisa realizada para: {query}", f"Confianca: {confidence}."]
        for item in sources[:3]:
            excerpt = ((item.get("page") or {}).get("excerpt") or item.get("snippet") or "").strip()
            lines.append(f"- {item.get('title')}: {excerpt[:260]}")
        return "\n".join(lines)
