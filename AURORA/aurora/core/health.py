from __future__ import annotations

from pathlib import Path

from aurora.core.config import AuroraConfig
from aurora.core.resources import ResourceMonitor


class HealthMonitor:
    def __init__(self, config: AuroraConfig, resources: ResourceMonitor) -> None:
        self.config = config
        self.resources = resources

    def check(self) -> dict:
        snap = self.resources.snapshot()
        paths = self.config.paths
        obsidian_path = Path(self.config.obsidian.migrated_path)
        issues: list[str] = []
        if not Path(paths.isis_root).exists():
            issues.append("isis root missing")
        if not obsidian_path.exists():
            issues.append("obsidian vault missing")
        if self.config.obsidian.integration_mode != "READ_ONLY":
            issues.append("obsidian not read-only")
        if not self.config.privacy.offline_mode:
            issues.append("offline mode disabled")
        if snap.ram_available_mb < 1024:
            issues.append("low RAM")
        return {
            "status": "ok" if not issues else "warning",
            "issues": issues,
            "ram_available_mb": snap.ram_available_mb,
            "vram_available_mb": snap.vram_available_mb,
            "obsidian_mode": self.config.obsidian.integration_mode,
            "offline_mode": self.config.privacy.offline_mode,
        }
