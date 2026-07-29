import json

from aurora.cli import main
from aurora.core.config import ConfigStore
from aurora.core.runtime import AuroraRuntime


def test_config_store_creates_default_file(tmp_path):
    store = ConfigStore(tmp_path / "config.json")

    config = store.load()

    assert config.online_enabled is False
    assert (tmp_path / "config.json").exists()


def test_runtime_builds_components(tmp_path):
    runtime = AuroraRuntime(tmp_path)

    assert runtime.policy.profile.value == "CONTROLLED"
    assert runtime.router.route.__name__ == "route"


def test_cli_status_outputs_json(tmp_path, capsys):
    code = main(["--root", str(tmp_path), "status"])

    payload = json.loads(capsys.readouterr().out)
    assert code == 0
    assert payload["profile"] == "CONTROLLED"


def test_cli_route_outputs_decision(tmp_path, capsys):
    code = main(["--root", str(tmp_path), "route", "corrija este codigo"])

    payload = json.loads(capsys.readouterr().out)
    assert code == 0
    assert payload["profile"] == "CODING"


def test_cli_route_detects_plural_accented_code_prompt(tmp_path, capsys):
    code = main(["--root", str(tmp_path), "route", "voce consegue criar códigos"])

    payload = json.loads(capsys.readouterr().out)
    assert code == 0
    assert payload["profile"] == "CODING"


def test_cli_memory_confirmed_search(tmp_path, capsys):
    main(["--root", str(tmp_path), "memory-add", "AURORA registra memoria local", "--confirm"])
    capsys.readouterr()

    code = main(["--root", str(tmp_path), "memory-search", "AURORA"])
    payload = json.loads(capsys.readouterr().out)

    assert code == 0
    assert len(payload) == 1


def test_cli_voice_mock(tmp_path, capsys):
    code = main(["--root", str(tmp_path), "voice-mock", "--transcript", "teste"])

    payload = json.loads(capsys.readouterr().out)
    assert code == 0
    assert payload["transcript"] == "teste"
    assert payload["audio"].endswith("tts_mock.wav")


def test_cli_core_status(tmp_path, capsys):
    code = main(["--root", str(tmp_path), "core", "status"])

    payload = json.loads(capsys.readouterr().out)
    assert code == 0
    assert payload["command_type"] == "status"
