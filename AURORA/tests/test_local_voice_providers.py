from pathlib import Path

import pytest

from aurora.voice.local_providers import ConfiguredWakeWordProvider, PiperTextToSpeechProvider, WhisperCppSpeechToTextProvider


def test_configured_wake_word_can_be_disabled():
    provider = ConfiguredWakeWordProvider(enabled=False)

    assert provider.detect(b"sem palavra") is True


def test_whisper_provider_reports_missing_binary(tmp_path):
    provider = WhisperCppSpeechToTextProvider(Path("missing.exe"), tmp_path / "model.bin")

    with pytest.raises(FileNotFoundError):
        provider.transcribe(b"audio")


def test_piper_provider_reports_missing_voice(tmp_path):
    binary = tmp_path / "piper.exe"
    binary.write_text("", encoding="utf-8")
    provider = PiperTextToSpeechProvider(binary, tmp_path / "voice.onnx", tmp_path)

    with pytest.raises(FileNotFoundError):
        provider.synthesize("ola", "pt-BR")
