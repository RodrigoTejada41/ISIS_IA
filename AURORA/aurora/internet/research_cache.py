from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path


class ResearchCache:
    def __init__(self, cache_dir: Path) -> None:
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def key(self, query: str, mode: str, provider: str) -> str:
        payload = json.dumps({"query": query, "mode": mode, "provider": provider, "day": time.strftime("%Y-%m-%d")}, ensure_ascii=False, sort_keys=True)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def get(self, key: str, ttl_seconds: int) -> dict | None:
        path = self.cache_dir / f"{key}.json"
        if not path.exists() or time.time() - path.stat().st_mtime > ttl_seconds:
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def put(self, key: str, payload: dict) -> None:
        (self.cache_dir / f"{key}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def clear(self) -> int:
        count = 0
        for path in self.cache_dir.glob("*.json"):
            path.unlink(missing_ok=True)
            count += 1
        return count
