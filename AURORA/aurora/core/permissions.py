from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum


class PrivilegeProfile(str, Enum):
    MEDIUM = "MEDIUM"
    CONTROLLED = "CONTROLLED"
    TOTAL = "TOTAL"


class AuthorizationMode(str, Enum):
    AUTO_ALLOW = "AUTO_ALLOW"
    ASK_CONFIRMATION = "ASK_CONFIRMATION"
    REQUIRE_STRONG_CONFIRMATION = "REQUIRE_STRONG_CONFIRMATION"
    DENY = "DENY"


class ActionRisk(str, Enum):
    READ_ONLY = "READ_ONLY"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


IRREVERSIBLE_PERMISSIONS = {
    "disk.format",
    "database.drop",
    "backup.delete",
    "partition.delete",
    "security.disable",
    "finance.transfer",
    "purchase.create",
    "production.deploy",
}


@dataclass(slots=True)
class CustomPermissionRules:
    allowed_permissions: set[str] = field(default_factory=set)
    blocked_permissions: set[str] = field(default_factory=set)
    protected_folders: set[str] = field(default_factory=set)
    allowed_folders: set[str] = field(default_factory=set)
    allowed_domains: set[str] = field(default_factory=set)
    blocked_commands: set[str] = field(default_factory=set)


@dataclass
class PermissionPolicy:
    profile: PrivilegeProfile = PrivilegeProfile.CONTROLLED
    custom: CustomPermissionRules = field(default_factory=CustomPermissionRules)
    total_until: float | None = None
    previous_profile: PrivilegeProfile = PrivilegeProfile.CONTROLLED
    emergency_active: bool = False

    def set_profile(self, profile: PrivilegeProfile, authenticated: bool, duration_seconds: int | None = None) -> None:
        if not authenticated:
            raise PermissionError("profile change requires authentication")
        self.previous_profile = self.profile
        self.profile = profile
        self.total_until = time.time() + duration_seconds if profile == PrivilegeProfile.TOTAL and duration_seconds else None

    def expire_if_needed(self) -> None:
        if self.profile == PrivilegeProfile.TOTAL and self.total_until and time.time() >= self.total_until:
            self.profile = self.previous_profile
            self.total_until = None

    def emergency_stop(self) -> None:
        self.emergency_active = True
        self.profile = PrivilegeProfile.MEDIUM
        self.total_until = None

    def authorize(self, permission: str, risk: ActionRisk, destructive: bool = False) -> AuthorizationMode:
        self.expire_if_needed()
        if self.emergency_active:
            return AuthorizationMode.DENY
        if permission in self.custom.blocked_permissions or permission in IRREVERSIBLE_PERMISSIONS:
            return AuthorizationMode.REQUIRE_STRONG_CONFIRMATION
        if risk in {ActionRisk.HIGH, ActionRisk.CRITICAL} or destructive:
            return AuthorizationMode.REQUIRE_STRONG_CONFIRMATION

        if self.profile == PrivilegeProfile.MEDIUM:
            if risk in {ActionRisk.READ_ONLY, ActionRisk.LOW} and permission.endswith(".read"):
                return AuthorizationMode.AUTO_ALLOW
            return AuthorizationMode.DENY if destructive else AuthorizationMode.ASK_CONFIRMATION

        if self.profile == PrivilegeProfile.CONTROLLED:
            if risk in {ActionRisk.READ_ONLY, ActionRisk.LOW}:
                return AuthorizationMode.AUTO_ALLOW
            return AuthorizationMode.ASK_CONFIRMATION

        if permission in self.custom.allowed_permissions or risk in {ActionRisk.READ_ONLY, ActionRisk.LOW, ActionRisk.MEDIUM}:
            return AuthorizationMode.AUTO_ALLOW
        return AuthorizationMode.ASK_CONFIRMATION
