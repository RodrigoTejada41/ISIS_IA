from __future__ import annotations

from pathlib import Path

from aurora.voice.tts.external_cli_engine import ExternalCliTTSEngine
from aurora.voice.tts.piper_engine import AudioCache


class ChatterboxTTSEngine(ExternalCliTTSEngine):
    def __init__(self, model_dir: Path, output_dir: Path, command_args: list[str] | None = None, voice: str = "", cache: AudioCache | None = None) -> None:
        super().__init__(
            name="chatterbox",
            model_dir=model_dir,
            output_dir=output_dir,
            command_args=command_args,
            voice=voice,
            supports_streaming=False,
            supports_emotion=True,
            cache=cache,
        )
