from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from aurora.internet.domain_policy import DomainPolicy
from aurora.permissions.permission_engine import ActionContext, PermissionEngine


@dataclass(slots=True)
class DownloadResult:
    ok: bool
    status: str
    url: str
    destination: str = ""
    sha256: str = ""
    size_bytes: int = 0
    error: str = ""


class DownloadManager:
    def __init__(self, config, storage_root: Path) -> None:
        self.config = config
        self.storage_root = storage_root
        self.download_dir = storage_root / "data" / "downloads"
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.permissions = PermissionEngine(config, storage_root / "config" / "permissions")
        self.domain_policy = DomainPolicy(config.internet.allowed_domains, config.internet.trusted_domains, config.internet.blocked_domains, config.internet.allow_private_networks)

    def download(self, url: str, confirmed: bool = False) -> DownloadResult:
        parsed = urlparse(url)
        suffix = Path(parsed.path).suffix.lower()
        if suffix in self.config.internet.blocked_extensions:
            return DownloadResult(False, "blocked", url, error=f"Tipo bloqueado: {suffix}")
        domain = self.domain_policy.validate_url(url)
        if not domain.allowed:
            return DownloadResult(False, "blocked", url, error=domain.reason)
        decision = self.permissions.evaluate(ActionContext("internet.download", url, confirmed=confirmed, risk="HIGH"))
        if decision.status == "confirm":
            return DownloadResult(False, "needs_confirmation", url, error=decision.reason)
        if decision.is_denied:
            return DownloadResult(False, "blocked", url, error=decision.reason)
        name = Path(parsed.path).name or f"download_{int(time.time())}.bin"
        target = self.download_dir / name
        request = Request(url, headers={"User-Agent": "ISIS-safe-download/1.0", "Accept-Encoding": "identity"})
        with urlopen(request, timeout=self.config.internet.timeout_seconds) as response:
            size_header = response.headers.get("content-length")
            if size_header and int(size_header) > self.config.internet.max_download_mb * 1024 * 1024:
                return DownloadResult(False, "blocked", url, error="Arquivo acima do limite configurado")
            data = response.read(self.config.internet.max_download_mb * 1024 * 1024 + 1)
        if len(data) > self.config.internet.max_download_mb * 1024 * 1024:
            return DownloadResult(False, "blocked", url, error="Arquivo acima do limite configurado")
        target.write_bytes(data)
        digest = hashlib.sha256(data).hexdigest()
        return DownloadResult(True, "downloaded", url, str(target), digest, len(data))
