from __future__ import annotations

from dataclasses import dataclass

from aurora.automation.ui import UIAction, UIActionResult, UIActionStatus, UIActionType, UIAutomationService
from aurora.perception.screen import ScreenAnalyzer, ScreenFrame


@dataclass(slots=True)
class ScreenActionSuggestion:
    instruction: str
    action: UIAction
    confidence: float
    reason: str


class ScreenAutomationBridge:
    def __init__(self, analyzer: ScreenAnalyzer | None = None, automation: UIAutomationService | None = None) -> None:
        self.analyzer = analyzer or ScreenAnalyzer()
        self.automation = automation or UIAutomationService()

    def suggest(self, frame: ScreenFrame, instruction: str) -> ScreenActionSuggestion:
        analysis = self.analyzer.analyze(frame)
        normalized = instruction.lower()
        for button in analysis.detected_buttons:
            if self._matches(normalized, button):
                return ScreenActionSuggestion(instruction, UIAction(UIActionType.CLICK, button), 0.9, "matched detected button")
        for field in analysis.detected_fields:
            if "digite" in normalized or "type" in normalized:
                value = instruction.split(":", 1)[1].strip() if ":" in instruction else ""
                return ScreenActionSuggestion(instruction, UIAction(UIActionType.TYPE_TEXT, field, value), 0.75, "matched detected field")
        planned = self.automation.plan_from_instruction(instruction)[0]
        return ScreenActionSuggestion(instruction, planned, 0.4, "fallback planner")

    def suggest_and_execute_mock(self, frame: ScreenFrame, instruction: str, approved: bool) -> UIActionResult:
        suggestion = self.suggest(frame, instruction)
        if suggestion.confidence < 0.5:
            return UIActionResult(UIActionStatus.BLOCKED, suggestion.action, "low confidence")
        return self.automation.execute(suggestion.action, approved=approved)

    @staticmethod
    def _matches(instruction: str, detected_text: str) -> bool:
        tokens = {token for token in detected_text.lower().replace("botao", "").replace("botão", "").split() if len(token) > 2}
        return any(token in instruction for token in tokens)
