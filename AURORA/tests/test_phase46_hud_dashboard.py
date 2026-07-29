import json
import subprocess
import sys

from aurora.core.config import AuroraConfig, ConfigStore
from aurora.core.runtime import AuroraRuntime
from aurora.ui.hud_dashboard import build_hud_snapshot


def test_hud_snapshot_contains_operational_models(tmp_path):
    config = AuroraConfig()
    config.paths.isis_root = str(tmp_path / "ISIS")
    ConfigStore(tmp_path / "data" / "config.json").save(config)

    snapshot = build_hud_snapshot(AuroraRuntime(tmp_path))

    assert snapshot.assistant_name == "ISIS"
    assert snapshot.embedding_model
    assert isinstance(snapshot.ollama_models, list)


def test_ui_hud_snapshot_cli_outputs_json(tmp_path):
    config = AuroraConfig()
    config.paths.isis_root = str(tmp_path / "ISIS")
    ConfigStore(tmp_path / "data" / "config.json").save(config)

    result = subprocess.run(
        [sys.executable, "-m", "aurora.cli", "--root", str(tmp_path), "ui-hud-snapshot"],
        capture_output=True,
        text=True,
        timeout=30,
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 0
    assert payload["assistant_name"] == "ISIS"
    assert "project_embeddings_pending" in payload
