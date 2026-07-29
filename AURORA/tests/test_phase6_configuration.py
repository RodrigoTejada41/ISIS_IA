import json

from scripts.phase6_configure_isis import configure


def test_phase6_writes_read_only_config(tmp_path):
    code_config = tmp_path / "code_config.json"
    isis_config = tmp_path / "isis" / "config" / "isis_config.json"
    validation = tmp_path / "validation.json"
    validation.write_text(json.dumps({"status": "warning"}), encoding="utf-8")

    report = configure(code_config, isis_config, validation, min_free_gb=0)
    payload = json.loads(isis_config.read_text(encoding="utf-8"))

    assert report["status"] == "configured"
    assert payload["assistant_name"] == "ISIS"
    assert payload["obsidian"]["integration_mode"] == "READ_ONLY"
    assert payload["obsidian"]["allow_note_writes"] is False
    assert payload["privacy"]["internet_enabled"] is False
