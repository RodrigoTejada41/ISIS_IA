from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from aurora.core.auth import LocalAuthenticator
from aurora.core.permissions import PrivilegeProfile
from aurora.core.privilege_audit import PrivilegeAuditLogger, PrivilegeAuditRecord
from aurora.core.runtime import AuroraRuntime


@dataclass(slots=True)
class PrivilegeControlState:
    current_profile: str
    available_profiles: list[str]
    auth_configured: bool
    editable: bool
    reason: str


@dataclass(slots=True)
class PrivilegeChangeResult:
    changed: bool
    profile: str
    reason: str


class PrivilegeControlService:
    def __init__(
        self,
        runtime: AuroraRuntime,
        authenticator: LocalAuthenticator | None = None,
        audit: PrivilegeAuditLogger | None = None,
    ) -> None:
        self.runtime = runtime
        self.authenticator = authenticator or LocalAuthenticator(Path(runtime.config.paths.isis_root) / "config" / "auth.json")
        self.audit = audit or PrivilegeAuditLogger(Path(runtime.config.paths.isis_root) / "logs" / "security" / "privileges.jsonl")

    def state(self) -> PrivilegeControlState:
        auth_status = self.authenticator.status()
        return PrivilegeControlState(
            current_profile=self.runtime.policy.profile.value,
            available_profiles=[profile.value for profile in PrivilegeProfile],
            auth_configured=auth_status.configured,
            editable=auth_status.configured,
            reason="ready" if auth_status.configured else "local authentication is not configured",
        )

    def change_profile(self, profile: str, password: str) -> PrivilegeChangeResult:
        state = self.state()
        if not state.editable:
            self._record("profile.change", self.runtime.policy.profile.value, self.runtime.policy.profile.value, False, state.reason)
            return PrivilegeChangeResult(False, self.runtime.policy.profile.value, state.reason)
        if profile not in state.available_profiles:
            self._record("profile.change", self.runtime.policy.profile.value, self.runtime.policy.profile.value, False, "invalid profile")
            return PrivilegeChangeResult(False, self.runtime.policy.profile.value, "invalid profile")
        if not self.authenticator.verify_password(password):
            self._record("profile.change", self.runtime.policy.profile.value, self.runtime.policy.profile.value, False, "authentication failed")
            return PrivilegeChangeResult(False, self.runtime.policy.profile.value, "authentication failed")
        previous = self.runtime.policy.profile.value
        self.runtime.policy.set_profile(PrivilegeProfile(profile), authenticated=True)
        self.runtime.save_config()
        self._record("profile.change", previous, self.runtime.policy.profile.value, True, "profile changed")
        return PrivilegeChangeResult(True, self.runtime.policy.profile.value, "profile changed")

    def emergency_stop(self) -> PrivilegeChangeResult:
        previous = self.runtime.policy.profile.value
        self.runtime.policy.emergency_stop()
        self.runtime.save_config()
        self._record("emergency.stop", previous, self.runtime.policy.profile.value, True, "emergency stop")
        return PrivilegeChangeResult(True, self.runtime.policy.profile.value, "emergency stop")

    def _record(self, action: str, previous: str, new: str, success: bool, reason: str) -> None:
        self.audit.record(PrivilegeAuditRecord(action, previous, new, success, reason))
