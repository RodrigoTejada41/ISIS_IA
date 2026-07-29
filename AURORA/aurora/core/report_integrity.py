from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass(slots=True)
class ReportHash:
    path: str
    sha256: str
    bytes: int


@dataclass(slots=True)
class ReportIntegrityManifest:
    generated_at: str
    root: str
    reports: list[ReportHash]


class ReportIntegrityService:
    def __init__(self, reports_root: str | Path) -> None:
        self.reports_root = Path(reports_root)

    def build_manifest(self, output_path: str | Path) -> ReportIntegrityManifest:
        reports = [
            self._hash_file(path)
            for path in sorted(self.reports_root.rglob("*"))
            if path.is_file() and path.name != Path(output_path).name and not path.name.endswith(".sig.json")
        ]
        manifest = ReportIntegrityManifest(datetime.now(timezone.utc).isoformat(), str(self.reports_root), reports)
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(asdict(manifest), ensure_ascii=False, indent=2), encoding="utf-8")
        return manifest

    def verify_manifest(self, manifest_path: str | Path) -> bool:
        payload = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
        for item in payload.get("reports", []):
            path = Path(item["path"])
            if not path.exists():
                return False
            if self._hash_file(path).sha256 != item["sha256"]:
                return False
        return True

    @staticmethod
    def _hash_file(path: Path) -> ReportHash:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        return ReportHash(str(path), digest, path.stat().st_size)
