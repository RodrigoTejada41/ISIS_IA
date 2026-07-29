import json
import subprocess
import sys

from aurora.core.config import AuroraConfig, ConfigStore
from aurora.core.runtime import AuroraRuntime
from aurora.ui.hud_dashboard import build_hud_snapshot


def test_voice_status_cli_reports_configured_piper_paths(tmp_path):
    config = AuroraConfig()
    config.paths.isis_root = str(tmp_path / "ISIS")
    config.voice.tts_engine = "piper"
    config.voice.piper_binary_path = str(tmp_path / "piper.exe")
    config.voice.piper_voice_path = str(tmp_path / "voice.onnx")
    ConfigStore(tmp_path / "data" / "config.json").save(config)

    result = subprocess.run(
        [sys.executable, "-m", "aurora.cli", "--root", str(tmp_path), "voice-status"],
        capture_output=True,
        text=True,
        timeout=30,
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 0
    assert payload["tts_engine"] == "piper"
    assert payload["piper_binary_exists"] is False
    assert payload["piper_voice_exists"] is False


def test_hud_snapshot_includes_voice_status(tmp_path):
    config = AuroraConfig()
    config.paths.isis_root = str(tmp_path / "ISIS")
    config.voice.tts_engine = "mock"
    ConfigStore(tmp_path / "data" / "config.json").save(config)

    snapshot = build_hud_snapshot(AuroraRuntime(tmp_path))

    assert snapshot.tts_engine == "mock"
    assert snapshot.tts_ready is True
