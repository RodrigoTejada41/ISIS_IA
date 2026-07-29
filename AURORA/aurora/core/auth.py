from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
from dataclasses import dataclass
from pathlib import Path


AUTH_ENV_VAR = "ISIS_ADMIN_PASSWORD"


@dataclass(frozen=True, slots=True)
class AuthStatus:
    configured: bool
    env_var: str
    iterations: int


class LocalAuthenticator:
    def __init__(self, path: str | Path, iterations: int = 390_000) -> None:
        self.path = Path(path)
        self.iterations = iterations

    def status(self) -> AuthStatus:
        return AuthStatus(self.path.exists(), AUTH_ENV_VAR, self.iterations)

    def bootstrap_from_env(self, overwrite: bool = False) -> AuthStatus:
        if self.path.exists() and not overwrite:
            return self.status()
        password = os.environ.get(AUTH_ENV_VAR, "")
        if len(password) < 12:
            raise PermissionError(f"{AUTH_ENV_VAR} must contain at least 12 characters")
        salt = secrets.token_bytes(16)
        digest = self._hash(password, salt, self.iterations)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "algorithm": "pbkdf2_sha256",
            "iterations": self.iterations,
            "salt": base64.b64encode(salt).decode("ascii"),
            "hash": base64.b64encode(digest).decode("ascii"),
        }
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return self.status()

    def verify_env(self) -> bool:
        password = os.environ.get(AUTH_ENV_VAR, "")
        return self.verify_password(password)

    def verify_password(self, password: str) -> bool:
        if not password or not self.path.exists():
            return False
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        salt = base64.b64decode(payload["salt"])
        expected = base64.b64decode(payload["hash"])
        iterations = int(payload["iterations"])
        return hmac.compare_digest(self._hash(password, salt, iterations), expected)

    @staticmethod
    def _hash(password: str, salt: bytes, iterations: int) -> bytes:
        return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
