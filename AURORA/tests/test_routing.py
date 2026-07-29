from aurora.core.audit import AuditLogger
from aurora.core.resources import ResourceLimits, ResourceMonitor
from aurora.core.routing import ModelProfile, ModelRouter, ModelSpec, RouteRequest


class FixedResources(ResourceMonitor):
    def __init__(self, can_load=True):
        self._can_load = can_load

    def can_load(self, estimated_model_mb, context_mb, limits):
        return self._can_load, "ok" if self._can_load else "insufficient VRAM"


def router(tmp_path, can_load=True):
    return ModelRouter(
        [
            ModelSpec("fast-local", {ModelProfile.FAST, ModelProfile.GENERAL}, 2500, priority=1),
            ModelSpec("code-local", {ModelProfile.CODING}, 6000, priority=1),
            ModelSpec("vision-local", {ModelProfile.VISION}, 7000, priority=1),
        ],
        FixedResources(can_load),
        AuditLogger(tmp_path / "audit.jsonl"),
        ResourceLimits(),
    )


def test_selects_coding_profile_for_code(tmp_path):
    decision = router(tmp_path).route(RouteRequest("corrija este código: ```python\nprint(1)\n```"))

    assert decision.profile == ModelProfile.CODING
    assert decision.model and decision.model.model_id == "code-local"


def test_selects_vision_profile_for_image(tmp_path):
    decision = router(tmp_path).route(RouteRequest("descreva", has_image=True))

    assert decision.profile == ModelProfile.VISION
    assert decision.model and decision.model.model_id == "vision-local"


def test_manual_model_selection(tmp_path):
    decision = router(tmp_path).route(RouteRequest("ola", manual_model_id="code-local"))

    assert decision.reason == "manual model selected"
    assert decision.model and decision.model.model_id == "code-local"


def test_unavailable_model_returns_clear_failure(tmp_path):
    decision = router(tmp_path, can_load=False).route(RouteRequest("analise " * 300))

    assert decision.available is False
    assert decision.model is None
    assert decision.resource_reason == "no available model"
