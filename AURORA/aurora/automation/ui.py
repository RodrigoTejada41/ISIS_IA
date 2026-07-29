from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class UIActionType(str, Enum):
    CLICK = "CLICK"
    TYPE_TEXT = "TYPE_TEXT"
    HOTKEY = "HOTKEY"
    SCROLL = "SCROLL"


class UIActionStatus(str, Enum):
    PLANNED = "PLANNED"
    EXECUTED = "EXECUTED"
    BLOCKED = "BLOCKED"


@dataclass(slots=True)
class UIAction:
    action_type: UIActionType
    target: str
    value: str = ""
    requires_approval: bool = True


@dataclass(slots=True)
class UIActionResult:
    status: UIActionStatus
    action: UIAction
    reason: str


@dataclass(slots=True)
class UIAutomationPolicy:
    real_execution_enabled: bool = False
    require_approval_per_action: bool = True
    blocked_targets: set[str] = field(default_factory=lambda: {"senha", "password", "banco", "bank", "formatar", "excluir conta"})
    blocked_values: set[str] = field(default_factory=lambda: {"senha", "password", "token", "api_key"})

    def allows(self, action: UIAction, approved: bool) -> tuple[bool, str]:
        target = action.target.lower()
        value = action.value.lower()
        if any(item in target for item in self.blocked_targets):
            return False, "target blocked by policy"
        if any(item in value for item in self.blocked_values):
            return False, "value blocked by policy"
        if self.require_approval_per_action and not approved:
            return False, "approval required"
        return True, "allowed"


class MockUIAutomationProvider:
    def __init__(self) -> None:
        self.executed: list[UIAction] = []

    def execute(self, action: UIAction) -> UIActionResult:
        self.executed.append(action)
        return UIActionResult(UIActionStatus.EXECUTED, action, "mock execution")


class UIAutomationService:
    def __init__(self, provider: MockUIAutomationProvider | None = None, policy: UIAutomationPolicy | None = None) -> None:
        self.provider = provider or MockUIAutomationProvider()
        self.policy = policy or UIAutomationPolicy()

    def plan_from_instruction(self, instruction: str) -> list[UIAction]:
        normalized = instruction.lower()
        if "digite" in normalized or "type" in normalized:
            value = instruction.split(":", 1)[1].strip() if ":" in instruction else instruction
            return [UIAction(UIActionType.TYPE_TEXT, "focused-field", value)]
        if "atalho" in normalized or "hotkey" in normalized:
            value = instruction.split(":", 1)[1].strip() if ":" in instruction else "ctrl+s"
            return [UIAction(UIActionType.HOTKEY, "keyboard", value)]
        if "rolar" in normalized or "scroll" in normalized:
            return [UIAction(UIActionType.SCROLL, "active-window", "down")]
        return [UIAction(UIActionType.CLICK, instruction.strip() or "unknown-target")]

    def execute(self, action: UIAction, approved: bool = False) -> UIActionResult:
        allowed, reason = self.policy.allows(action, approved)
        if not allowed:
            return UIActionResult(UIActionStatus.BLOCKED, action, reason)
        if not self.policy.real_execution_enabled:
            return UIActionResult(UIActionStatus.EXECUTED, action, "mock execution only")
        return self.provider.execute(action)
