import json

from aurora.cli import main
from aurora.core.assistant import IsisAssistantCore
from aurora.core.config import AuroraConfig
from aurora.core.audit import AuditLogger
from aurora.voice.factory import build_voice_session


def test_voice_factory_uses_mock_by_default(tmp_path):
    config = AuroraConfig()
    config.paths.temporary_dir = str(tmp_path)

    session = build_voice_session(config, AuditLogger(tmp_path / "audit.jsonl"), transcript="status")

    transcript, response, audio = session.run_once(lambda text: "ok", click_to_talk=True)
    assert transcript == "status"
    assert response == "ok"
    assert audio and audio.exists()


def test_core_voice_once_uses_core_generation(tmp_path):
    core = IsisAssistantCore(tmp_path)
    core.initialize()

    result = core.run_voice_once("corrija este codigo")

    assert result["transcript"] == "corrija este codigo"
    assert result["stt_engine"] == "mock"
    assert result["voice_engine"] == "mock"
    assert "coding-local-mock" in result["response"]


def test_cli_voice_core_outputs_json(tmp_path, capsys):
    code = main(["--root", str(tmp_path), "voice-core", "--transcript", "status"])

    payload = json.loads(capsys.readouterr().out)
    assert code == 0
    assert payload["transcript"] == "status"
    assert payload["audio_path"].endswith("tts_mock.wav")
