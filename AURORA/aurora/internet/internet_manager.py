from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from urllib.request import Request, urlopen

from aurora.internet.research_agent import ResearchAgent


class InternetManager:
    def __init__(self, config, storage_root: Path) -> None:
        self.config = config
        self.agent = ResearchAgent(config, storage_root)

    def status(self) -> dict:
        settings = self.config.internet
        return {
            "enabled": settings.enabled and not self.config.privacy.offline_mode,
            "mode": settings.mode,
            "provider": settings.search_provider,
            "automatic_search": settings.automatic_search,
            "max_results": settings.max_results,
            "max_pages": settings.max_pages,
            "allow_downloads": settings.allow_downloads,
            "trusted_domains": settings.trusted_domains,
            "allowed_domains": settings.allowed_domains,
            "blocked_domains": settings.blocked_domains,
        }

    def test_connection(self) -> dict:
        if not self.status()["enabled"]:
            return {"ok": False, "status": "blocked", "error": "Internet bloqueada pela configuracao."}
        try:
            request = Request("https://example.com", headers={"User-Agent": "ISIS-connectivity-check/1.0"})
            with urlopen(request, timeout=self.config.internet.timeout_seconds) as response:
                return {"ok": True, "status": "online", "http_status": response.status}
        except Exception as exc:
            return {"ok": False, "status": "error", "error": str(exc)}
