from __future__ import annotations

import base64
import hmac
import json
import secrets
import shutil
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path


@dataclass(slots=True)
class SignatureResult:
    ok: bool
    path: str
    signature: str
    key_id: str


@dataclass(slots=True)
class SignatureKeyStatus:
    configured: bool
    path: str
    key_id: str | None
    bytes: int
    backup_count: int
    read_only: bool


@dataclass(slots=True)
class SignatureKeyRotationResult:
    rotated: bool
    old_key_id: str | None
    new_key_id: str
    backup_path: str | None


class LocalSignatureService:
    def __init__(self, key_path: str | Path) -> None:
        self.key_path = Path(key_path)

    def ensure_key(self) -> str:
        if self.key_path.exists():
            payload = json.loads(self.key_path.read_text(encoding="utf-8"))
            return str(payload["key_id"])
        return self._write_new_key()

    def status(self) -> SignatureKeyStatus:
        if not self.key_path.exists():
            return SignatureKeyStatus(False, str(self.key_path), None, 0, self._backup_count(), False)
        payload = json.loads(self.key_path.read_text(encoding="utf-8"))
        return SignatureKeyStatus(
            True,
            str(self.key_path),
            str(payload["key_id"]),
            self.key_path.stat().st_size,
            self._backup_count(),
            not bool(self.key_path.stat().st_mode & 0o200),
        )

    def rotate_key(self) -> SignatureKeyRotationResult:
        old_key_id: str | None = None
        backup_path: str | None = None
        if self.key_path.exists():
            payload = json.loads(self.key_path.read_text(encoding="utf-8"))
            old_key_id = str(payload["key_id"])
            backup = self.key_path.with_name(f"{self.key_path.stem}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.bak.json")
            shutil.copy2(self.key_path, backup)
            backup_path = str(backup)
        new_key_id = self._write_new_key()
        return SignatureKeyRotationResult(True, old_key_id, new_key_id, backup_path)

    def sign_file(self, file_path: str | Path, output_path: str | Path) -> SignatureResult:
        key_id, key = self._load_or_create_key()
        target = Path(file_path)
        signature = hmac.new(key, target.read_bytes(), sha256).hexdigest()
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        result = SignatureResult(True, str(target), signature, key_id)
        output.write_text(
            json.dumps({**asdict(result), "algorithm": "hmac_sha256", "created_at": datetime.now(timezone.utc).isoformat()}, indent=2),
            encoding="utf-8",
        )
        return result

    def verify_file(self, file_path: str | Path, signature_path: str | Path) -> bool:
        key_id, key = self._load_or_create_key()
        payload = json.loads(Path(signature_path).read_text(encoding="utf-8"))
        if payload.get("key_id") != key_id:
            return False
        signature = hmac.new(key, Path(file_path).read_bytes(), sha256).hexdigest()
        return hmac.compare_digest(signature, payload.get("signature", ""))

    def _load_or_create_key(self) -> tuple[str, bytes]:
        self.ensure_key()
        payload = json.loads(self.key_path.read_text(encoding="utf-8"))
        return str(payload["key_id"]), base64.b64decode(payload["key"])

    def _write_new_key(self) -> str:
        key = secrets.token_bytes(32)
        key_id = secrets.token_hex(8)
        self.key_path.parent.mkdir(parents=True, exist_ok=True)
        self.key_path.write_text(json.dumps({"key_id": key_id, "key": base64.b64encode(key).decode("ascii")}, indent=2), encoding="utf-8")
        return key_id

    def _backup_count(self) -> int:
        if not self.key_path.parent.exists():
            return 0
        return len(list(self.key_path.parent.glob(f"{self.key_path.stem}_*.bak.json")))
