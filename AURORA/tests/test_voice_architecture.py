import sys
from pathlib import Path

from aurora.core.audit import AuditLogger
from aurora.voice.interruption_manager import InterruptionManager
from aurora.voice.text_normalizer import PortugueseSpeechNormalizer
from aurora.voice.tts.base_tts import TTSEngineInfo, TTSResult
from aurora.voice.tts.kokoro_engine import KokoroTTSEngine
from aurora.voice.tts.piper_engine import AudioCache
from aurora.voice.vad_service import VoiceActivityDetector
from aurora.voice.voice_router import VoiceRouter


def test_portuguese_speech_normalizer_hides_paths_and_http():
    text = r"A requisicao retornou HTTP 200. O arquivo esta em C:\Users\Rodrigo\Desktop\projeto."

    speech = PortugueseSpeechNormalizer().normalize(text)

    assert "operacao foi concluida com sucesso" in speech
    assert "C:\\Users" not in speech
    assert "caminho local indicado" in speech


def test_audio_cache_reuses_same_voice_parameters(tmp_path):
    cache = AudioCache(tmp_path, max_files=2)
    source = tmp_path / "source.wav"
    source.write_bytes(b"audio")
    key = cache.key("Bom dia", "piper", "dii", 1.0, "friendly")

    cached = cache.put(key, source)

    assert cached.exists()
    assert cache.get(key) == cached


class _FailingEngine:
    name = "broken"

    def is_available(self):
        return True

    def synthesize(self, *args, **kwargs):
        raise RuntimeError("broken")

    def stop(self):
        return

    def info(self):
        return TTSEngineInfo(name=self.name, voice="x", available=True)


class _WorkingEngine:
    name = "working"

    def __init__(self, path: Path):
        self.path = path

    def is_available(self):
        return True

    def synthesize(self, *args, **kwargs):
        self.path.write_bytes(b"ok")
        return TTSResult(self.path, self.name, "voice", 1)

    def stop(self):
        return

    def info(self):
        return TTSEngineInfo(name=self.name, voice="voice", available=True)


def test_voice_router_falls_back_to_next_engine(tmp_path):
    router = VoiceRouter([_FailingEngine(), _WorkingEngine(tmp_path / "out.wav")], AuditLogger(tmp_path / "audit.jsonl"))

    result = router.synthesize("teste")

    assert result is not None
    assert result.engine == "working"
    assert result.audio_path.exists()


def test_kokoro_cli_engine_is_available_when_command_is_configured(tmp_path):
    engine = KokoroTTSEngine(
        model_dir=tmp_path,
        output_dir=tmp_path,
        command_args=[
            sys.executable,
            "-c",
            "from pathlib import Path; import sys; Path(sys.argv[1]).write_bytes(b'audio')",
            "{output}",
        ],
        voice="pt-BR-test",
    )

    result = engine.synthesize("Bom dia")

    assert engine.is_available() is True
    assert result.engine == "kokoro"
    assert result.voice == "pt-BR-test"
    assert result.audio_path.exists()


def test_interruption_uses_vad_after_cooldown():
    vad = VoiceActivityDetector(min_bytes=4, threshold=1)
    manager = InterruptionManager(vad=vad, enabled=True, cooldown_seconds=0)
    manager.mark_speaking_started()

    assert manager.should_interrupt(bytes([0, 255, 0, 255])) is True
