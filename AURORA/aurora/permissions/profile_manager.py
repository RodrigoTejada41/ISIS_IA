from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass(slots=True)
class PermissionProfile:
    name: str
    internet_mode: str
    max_results: int = 5
    max_pages: int = 3
    allow_downloads: bool = False
    require_memory_confirmation: bool = True
    trusted_domains: list[str] = field(default_factory=list)


DEFAULT_PROFILES = [
    PermissionProfile("Offline Total", "blocked", 0, 0, False, True),
    PermissionProfile("Pesquisa Controlada", "controlled", 5, 3, False, True, ["python.org", "github.com", "microsoft.com"]),
    PermissionProfile("Pesquisa Tecnica", "controlled", 10, 6, False, True, ["python.org", "github.com", "docs.github.com", "microsoft.com", "nvidia.com"]),
    PermissionProfile("Projeto Ativo", "controlled", 8, 5, False, True),
    PermissionProfile("Desenvolvimento", "expanded", 12, 8, False, True, ["github.com", "pypi.org", "python.org"]),
    PermissionProfile("Privacidade Maxima", "controlled", 3, 2, False, True),
    PermissionProfile("Personalizado", "controlled", 5, 3, False, True),
]


class PermissionProfileManager:
    def __init__(self, storage_dir: Path) -> None:
        self.storage_dir = storage_dir
        self.path = storage_dir / "profiles.json"
        self.version_path = storage_dir / "profile_versions.jsonl"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.save_profiles(DEFAULT_PROFILES, "bootstrap")

    def list_profiles(self) -> list[dict]:
        return [asdict(item) for item in self.load_profiles()]

    def load_profiles(self) -> list[PermissionProfile]:
        data = json.loads(self.path.read_text(encoding="utf-8"))
        return [PermissionProfile(**item) for item in data]

    def save_profiles(self, profiles: list[PermissionProfile], reason: str) -> None:
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps([asdict(item) for item in profiles], ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(self.path)
        with self.version_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps({"timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"), "reason": reason, "profiles": [asdict(item) for item in profiles]}, ensure_ascii=False) + "\n")
