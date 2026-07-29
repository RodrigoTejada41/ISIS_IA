from aurora.core.audit import AuditLogger
from aurora.voice.audio import AudioInputManager, AudioOutputManager
from aurora.voice.providers import MockSpeechToTextProvider, MockTextToSpeechProvider, MockWakeWordProvider
from aurora.voice.session import VoiceSessionManager


def test_voice_flow_with_mocks(tmp_path):
    session = VoiceSessionManager(
        MockWakeWordProvider(),
        MockSpeechToTextProvider("qual o status"),
        MockTextToSpeechProvider(tmp_path),
        AudioInputManager(),
        AudioOutputManager(),
        AuditLogger(tmp_path / "audit.jsonl"),
    )

    transcript, response, output = session.run_once(lambda text: f"resposta para {text}")

    assert transcript == "qual o status"
    assert response == "resposta para qual o status"
    assert output and output.exists()


def test_voice_interrupt_command_stops_output(tmp_path):
    tts = MockTextToSpeechProvider(tmp_path)
    audio_out = AudioOutputManager()
    session = VoiceSessionManager(
        MockWakeWordProvider(),
        MockSpeechToTextProvider("pare"),
        tts,
        AudioInputManager(),
        audio_out,
        AuditLogger(tmp_path / "audit.jsonl"),
    )

    transcript, response, output = session.run_once(lambda text: "nao deve responder")

    assert transcript == "pare"
    assert response == ""
    assert output is None
    assert tts.stopped is True
    assert audio_out.stop_event.is_set()


def test_unavailable_microphone_raises(tmp_path):
    session = VoiceSessionManager(
        MockWakeWordProvider(),
        MockSpeechToTextProvider(),
        MockTextToSpeechProvider(tmp_path),
        AudioInputManager(device_name="invalid"),
        AudioOutputManager(),
        AuditLogger(tmp_path / "audit.jsonl"),
    )

    try:
        session.run_once(lambda text: text)
    except RuntimeError as exc:
        assert "microphone unavailable" in str(exc)
    else:
        raise AssertionError("expected microphone error")
