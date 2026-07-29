from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from urllib.parse import urlparse

from aurora.core.permissions import PrivilegeProfile


@dataclass(slots=True)
class ActionContext:
    action: str
    resource: str = ""
    user_role: str = "OWNER"
    project: str = ""
    source: str = "text"
    confirmed: bool = False
    risk: str = "LOW"


@dataclass(slots=True)
class PermissionDecision:
    action: str
    status: str
    reason: str
    rule: str = ""
    requires_confirmation: bool = False
    risk: str = "LOW"

    @property
    def is_allowed(self) -> bool:
        return self.status == "allow"

    @property
    def is_denied(self) -> bool:
        return self.status == "deny"


@dataclass(slots=True)
class TemporaryAuthorization:
    id: str
    action: str
    resource: str = ""
    project: str = ""
    expires_at: float = 0
    max_uses: int = 1
    used: int = 0

    def active_for(self, context: ActionContext) -> bool:
        if self.expires_at and time.time() > self.expires_at:
            return False
        if self.used >= self.max_uses:
            return False
        if self.action != context.action:
            return False
        if self.project and self.project != context.project:
            return False
        return not self.resource or self.resource in context.resource


class PermissionEngine:
    fixed_denies = {
        "execute_downloaded_file": "Regra fixa: nunca executar arquivo baixado automaticamente.",
        "self_authorize": "Regra fixa: a ISIS nao pode conceder permissao para si propria.",
        "erase_audit": "Regra fixa: historico de auditoria nao pode ser apagado silenciosamente.",
        "send_secret": "Regra fixa: credenciais e dados sensiveis nao podem ser enviados sem autorizacao.",
    }

    def __init__(self, config, storage_dir: Path) -> None:
        self.config = config
        self.storage_dir = storage_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.audit_path = self.storage_dir / "permission_history.jsonl"
        self.temporary_path = self.storage_dir / "temporary_permissions.json"
        self.temporary = self._load_temporary()

    def evaluate(self, context: ActionContext) -> PermissionDecision:
        settings = self.config.internet
        if context.action in self.fixed_denies:
            return self._record(context, PermissionDecision(context.action, "deny", self.fixed_denies[context.action], "fixed_security", risk="CRITICAL"))

        if context.action.startswith("internet.") and (not settings.enabled or settings.mode == "blocked" or self.config.privacy.offline_mode):
            return self._record(context, PermissionDecision(context.action, "deny", "Internet bloqueada pela configuracao atual.", "internet.mode", risk=context.risk))

        for auth in self.temporary:
            if auth.active_for(context):
                auth.used += 1
                self._save_temporary()
                return self._record(context, PermissionDecision(context.action, "allow", "Permitido por autorizacao temporaria ativa.", "temporary_authorization", risk=context.risk))

        if context.action in {"internet.download", "internet.upload", "memory.permanent_save", "site.login"}:
            if context.confirmed:
                return self._record(context, PermissionDecision(context.action, "allow", "Permitido apos confirmacao explicita.", "confirmed_action", risk="HIGH"))
            return self._record(context, PermissionDecision(context.action, "confirm", "Acao sensivel exige confirmacao.", "sensitive_action", True, "HIGH"))

        profile = PrivilegeProfile(self.config.profile)
        if profile == PrivilegeProfile.CONTROLLED:
            if context.confirmed:
                return self._record(context, PermissionDecision(context.action, "allow", "Permitido apos confirmacao no perfil CONTROLLED.", "profile_controlled", risk=context.risk))
            return self._record(context, PermissionDecision(context.action, "confirm", "Perfil CONTROLLED exige confirmacao para acesso externo.", "profile_controlled", True, context.risk))

        if profile == PrivilegeProfile.MEDIUM:
            if context.action in {"internet.search", "internet.open_public", "source.read"}:
                return self._record(context, PermissionDecision(context.action, "allow", "Permitido pelo perfil MEDIUM para leitura publica.", "profile_medium", risk=context.risk))
            return self._record(context, PermissionDecision(context.action, "confirm", "Perfil MEDIUM exige confirmacao para esta acao.", "profile_medium", True, context.risk))

        if context.risk in {"CRITICAL", "HIGH"} and not context.confirmed:
            return self._record(context, PermissionDecision(context.action, "confirm", "Perfil TOTAL ainda exige confirmacao para alto risco.", "profile_total", True, context.risk))
        return self._record(context, PermissionDecision(context.action, "allow", "Permitido pelo perfil TOTAL dentro das regras fixas.", "profile_total", risk=context.risk))

    def emergency_block_all(self) -> dict:
        self.config.internet.enabled = False
        self.config.internet.mode = "blocked"
        self.config.privacy.internet_enabled = False
        self.config.privacy.offline_mode = True
        revoked = len(self.temporary)
        self.temporary = []
        self._save_temporary()
        self._write_audit({"action": "emergency_block_all", "result": "blocked", "revoked": revoked})
        return {"ok": True, "revoked": revoked, "internet": "blocked"}

    def add_temporary(self, action: str, resource: str = "", minutes: int = 60, max_uses: int = 1, project: str = "") -> TemporaryAuthorization:
        auth = TemporaryAuthorization(
            id=f"tmp-{int(time.time() * 1000)}",
            action=action,
            resource=resource,
            project=project,
            expires_at=time.time() + max(1, minutes) * 60,
            max_uses=max(1, max_uses),
        )
        self.temporary.append(auth)
        self._save_temporary()
        self._write_audit({"action": "temporary.add", "authorization": asdict(auth)})
        return auth

    def summary(self) -> dict:
        settings = self.config.internet
        return {
            "internet": settings.mode if settings.enabled and not self.config.privacy.offline_mode else "blocked",
            "profile": self.config.profile.value if hasattr(self.config.profile, "value") else str(self.config.profile),
            "search_provider": settings.search_provider,
            "automatic_search": settings.automatic_search,
            "downloads": "confirmation" if settings.allow_downloads else "blocked",
            "uploads": "blocked",
            "login": "blocked",
            "private_networks": "blocked" if not settings.allow_private_networks else "allowed_with_rules",
            "permanent_memory": "confirmation" if settings.require_memory_confirmation else "allowed_by_policy",
            "temporary_permissions": len([item for item in self.temporary if item.expires_at > time.time()]),
        }

    def simulate(self, context: ActionContext) -> dict:
        decision = self.evaluate(context)
        return {"action": context.action, "resource": context.resource, "decision": asdict(decision)}

    def _record(self, context: ActionContext, decision: PermissionDecision) -> PermissionDecision:
        self._write_audit({"context": asdict(context), "decision": asdict(decision)})
        return decision

    def _write_audit(self, payload: dict) -> None:
        payload = {"timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"), **payload}
        self.audit_path.parent.mkdir(parents=True, exist_ok=True)
        with self.audit_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(payload, ensure_ascii=False) + "\n")

    def _load_temporary(self) -> list[TemporaryAuthorization]:
        if not self.temporary_path.exists():
            return []
        try:
            data = json.loads(self.temporary_path.read_text(encoding="utf-8"))
            return [TemporaryAuthorization(**item) for item in data]
        except Exception:
            corrupt = self.temporary_path.with_suffix(".corrupt.json")
            self.temporary_path.replace(corrupt)
            return []

    def _save_temporary(self) -> None:
        tmp = self.temporary_path.with_suffix(".tmp")
        tmp.write_text(json.dumps([asdict(item) for item in self.temporary], ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(self.temporary_path)
