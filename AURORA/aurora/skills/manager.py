from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

from aurora.core.audit import AuditEvent, AuditLogger
from aurora.core.permissions import ActionRisk, AuthorizationMode, PermissionPolicy
from aurora.skills.manifest import SkillManifest


@dataclass(frozen=True, slots=True)
class SandboxResult:
    exit_code: int
    stdout: str
    stderr: str
    duration_ms: int
    modified_files: list[str]
    timed_out: bool = False


class SkillManager:
    def __init__(self, skills_dir: str | Path, policy: PermissionPolicy, audit: AuditLogger) -> None:
        self.skills_dir = Path(skills_dir)
        self.skills_dir.mkdir(parents=True, exist_ok=True)
        self.policy = policy
        self.audit = audit

    def load_manifest(self, skill_dir: str | Path) -> SkillManifest:
        manifest_path = Path(skill_dir) / "skill.json"
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest = SkillManifest.model_validate(data)
        self.audit.record(AuditEvent(action="skill.manifest.load", component="skills", params={"id": manifest.id}))
        return manifest

    def validate_permissions(self, manifest: SkillManifest) -> AuthorizationMode:
        worst = AuthorizationMode.AUTO_ALLOW
        for permission in manifest.permissions:
            mode = self.policy.authorize(permission.value, ActionRisk(manifest.risk_level.value))
            if mode == AuthorizationMode.DENY:
                return mode
            if mode == AuthorizationMode.REQUIRE_STRONG_CONFIRMATION:
                worst = mode
            elif mode == AuthorizationMode.ASK_CONFIRMATION and worst == AuthorizationMode.AUTO_ALLOW:
                worst = mode
        return worst

    def install_after_approval(self, staged_dir: str | Path, approved: bool, reason: str, author: str = "local") -> Path:
        manifest = self.load_manifest(staged_dir)
        if not approved:
            raise PermissionError("skill installation requires approval")
        target = self.skills_dir / manifest.name
        target.mkdir(parents=True, exist_ok=True)
        version_dir = target / "versions" / manifest.version
        version_dir.mkdir(parents=True, exist_ok=True)
        for item in Path(staged_dir).iterdir():
            if item.is_file():
                content = item.read_bytes()
                (target / item.name).write_bytes(content)
                (version_dir / item.name).write_bytes(content)
        checksum = self.checksum(target / manifest.entrypoint)
        self.audit.record(
            AuditEvent(
                action="skill.install",
                component="skills",
                params={"id": manifest.id, "version": manifest.version, "reason": reason, "author": author, "checksum": checksum},
                rollback_available=True,
            )
        )
        return target

    def rollback(self, skill_name: str, version: str) -> None:
        target = self.skills_dir / skill_name
        version_dir = target / "versions" / version
        if not version_dir.exists():
            raise FileNotFoundError(version)
        for item in version_dir.iterdir():
            if item.is_file():
                (target / item.name).write_bytes(item.read_bytes())
        self.audit.record(AuditEvent(action="skill.rollback", component="skills", params={"skill": skill_name, "version": version}))

    def run_in_sandbox(self, skill_dir: str | Path, args: dict | None = None, timeout_seconds: int | None = None) -> SandboxResult:
        manifest = self.load_manifest(skill_dir)
        timeout = timeout_seconds or manifest.timeout_seconds
        with tempfile.TemporaryDirectory(prefix="aurora_skill_") as tmp:
            workdir = Path(tmp)
            before = set(workdir.rglob("*"))
            started = time.time()
            try:
                proc = subprocess.run(
                    [sys.executable, str(Path(skill_dir) / manifest.entrypoint), json.dumps(args or {})],
                    cwd=workdir,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    env={"PYTHONIOENCODING": "utf-8"},
                )
                timed_out = False
                code = proc.returncode
                stdout = proc.stdout[-8000:]
                stderr = proc.stderr[-8000:]
            except subprocess.TimeoutExpired as exc:
                timed_out = True
                code = 124
                stdout = (exc.stdout or "")[-8000:] if isinstance(exc.stdout, str) else ""
                stderr = "timeout"
            after = set(workdir.rglob("*"))
            modified = [str(p) for p in after - before if p.is_file()]
            result = SandboxResult(code, stdout, stderr, int((time.time() - started) * 1000), modified, timed_out)
        self.audit.record(AuditEvent(action="skill.sandbox.run", component="skills", params={"id": manifest.id, "exit_code": result.exit_code}))
        return result

    @staticmethod
    def checksum(path: str | Path) -> str:
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()
