from aurora.core.audit import AuditEvent, AuditLogger
from aurora.core.resources import ResourceLimits, ResourceMonitor, ResourceSnapshot


def test_audit_sanitizes_sensitive_values(tmp_path):
    audit = AuditLogger(tmp_path / "audit.jsonl")
    audit.record(AuditEvent(action="auth", component="security", params={"password": "abc", "x": 1}))

    rows = audit.read_all()

    assert rows[0]["params"]["password"] == "***"
    assert rows[0]["params"]["x"] == 1


def test_resource_monitor_can_load_with_defaults():
    class FixedResourceMonitor(ResourceMonitor):
        def snapshot(self) -> ResourceSnapshot:
            return ResourceSnapshot(ram_total_mb=32768, ram_available_mb=24576, vram_total_mb=12288, vram_available_mb=8192)

    ok, reason = FixedResourceMonitor().can_load(estimated_model_mb=1024, context_mb=256, limits=ResourceLimits())

    assert ok is True
    assert reason == "resources available"


def test_resource_monitor_allows_ram_fallback_when_vram_is_low():
    class FixedResourceMonitor(ResourceMonitor):
        def snapshot(self) -> ResourceSnapshot:
            return ResourceSnapshot(ram_total_mb=32768, ram_available_mb=24576, vram_total_mb=12288, vram_available_mb=512)

    ok, reason = FixedResourceMonitor().can_load(estimated_model_mb=8500, context_mb=0, limits=ResourceLimits())

    assert ok is True
    assert reason == "VRAM insufficient; using RAM"
