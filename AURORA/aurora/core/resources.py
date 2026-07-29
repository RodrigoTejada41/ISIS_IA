from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ResourceSnapshot:
    ram_total_mb: int
    ram_available_mb: int
    vram_total_mb: int
    vram_available_mb: int
    cpu_percent: float | None = None


@dataclass(frozen=True, slots=True)
class ResourceLimits:
    max_ram_mb: int = 24 * 1024
    max_vram_mb: int = 10 * 1024
    max_loaded_models: int = 1
    keep_alive_seconds: int = 900
    prefer_gpu: bool = True
    unload_aggressiveness: str = "balanced"


class ResourceMonitor:
    def snapshot(self) -> ResourceSnapshot:
        ram_total, ram_available = self._ram_mb()
        vram_total, vram_free = self._vram_mb()
        return ResourceSnapshot(ram_total, ram_available, vram_total, vram_free)

    def can_load(self, estimated_model_mb: int, context_mb: int, limits: ResourceLimits) -> tuple[bool, str]:
        snap = self.snapshot()
        requested = estimated_model_mb + context_mb
        if requested > limits.max_ram_mb or requested > snap.ram_available_mb:
            return False, "insufficient RAM"
        if limits.prefer_gpu and snap.vram_total_mb and requested > min(limits.max_vram_mb, snap.vram_available_mb):
            return True, "VRAM insufficient; using RAM"
        return True, "resources available"

    def _ram_mb(self) -> tuple[int, int]:
        try:
            import psutil  # type: ignore

            mem = psutil.virtual_memory()
            return int(mem.total / 1048576), int(mem.available / 1048576)
        except Exception:
            total = 32 * 1024
            return total, max(1024, total - int(os.getpid() % 2048))

    def _vram_mb(self) -> tuple[int, int]:
        if not shutil.which("nvidia-smi"):
            return 12 * 1024, 9 * 1024
        try:
            out = subprocess.check_output(
                [
                    "nvidia-smi",
                    "--query-gpu=memory.total,memory.free",
                    "--format=csv,noheader,nounits",
                ],
                text=True,
                timeout=2,
            ).splitlines()[0]
            total, free = [int(part.strip()) for part in out.split(",")]
            return total, free
        except Exception:
            return 12 * 1024, 9 * 1024
