from __future__ import annotations

import json
import time
from pathlib import Path

from aurora.permissions.rule_parser import ParsedRules, RuleParser


class RuleActivationService:
    def __init__(self, config, config_store, storage_dir: Path) -> None:
        self.config = config
        self.config_store = config_store
        self.storage_dir = storage_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.history_path = self.storage_dir / "rule_versions.jsonl"

    def analyze(self, text: str) -> ParsedRules:
        return RuleParser().parse(text)

    def apply_text(self, text: str, confirmed: bool = False, user: str = "OWNER") -> dict:
        parsed = self.analyze(text)
        if parsed.warnings:
            return {"ok": False, "status": "needs_review", "warnings": parsed.warnings, "parsed": parsed.structured}
        if parsed.requires_confirmation and not confirmed:
            return {"ok": False, "status": "needs_confirmation", "risk": parsed.risk, "parsed": parsed.structured}

        before = self.config.model_dump(mode="json")
        structured = parsed.structured
        internet = structured.get("internet") or {}
        if "enabled" in internet:
            self.config.internet.enabled = bool(internet["enabled"])
            self.config.privacy.internet_enabled = bool(internet["enabled"])
            self.config.privacy.offline_mode = not bool(internet["enabled"])
        if internet.get("mode"):
            self.config.internet.mode = str(internet["mode"])
        limits = structured.get("limits") or {}
        if "max_pages_per_research" in limits:
            self.config.internet.max_pages = max(1, int(limits["max_pages_per_research"]))
        if "max_duration_minutes" in limits:
            self.config.internet.timeout_seconds = max(5, int(limits["max_duration_minutes"]) * 60)
        downloads = structured.get("downloads") or {}
        if "enabled" in downloads:
            self.config.internet.allow_downloads = bool(downloads["enabled"])
        domains = structured.get("domains") or {}
        for domain in domains.get("allowed", []):
            if domain not in self.config.internet.trusted_domains:
                self.config.internet.trusted_domains.append(domain)
        for domain in domains.get("blocked", []):
            if domain not in self.config.internet.blocked_domains:
                self.config.internet.blocked_domains.append(domain)

        self.config_store.save(self.config)
        after = self.config.model_dump(mode="json")
        record = {"timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"), "user": user, "raw_text": parsed.raw_text, "risk": parsed.risk, "before": before, "after": after, "parsed": parsed.structured}
        with self.history_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")
        return {"ok": True, "status": "active", "risk": parsed.risk, "parsed": parsed.structured}

    def history(self, limit: int = 20) -> list[dict]:
        if not self.history_path.exists():
            return []
        lines = self.history_path.read_text(encoding="utf-8").splitlines()[-limit:]
        return [json.loads(line) for line in reversed(lines) if line.strip()]
