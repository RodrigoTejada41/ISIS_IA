from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from aurora.core.audit import AuditEvent, AuditLogger
from aurora.voice.audio import AudioInputManager, AudioOutputManager
from aurora.voice.providers import SpeechToTextProvider, TextToSpeechProvider, WakeWordProvider


INTERRUPT_COMMANDS = {"pare", "cancelar", "silencio", "silêncio", "interromper"}


@dataclass
class VoiceSessionConfig:
    language: str = "pt-BR"
    selected_voice: str = "pt-BR-female-mock"
    response_mode: str = "text_and_voice"
    require_transcript_review: bool = False
    conversation_seconds: int = 120
    max_interactions: int = 10
    avoid_echo: bool = True


class VoiceSessionManager:
    def __init__(
        self,
        wake: WakeWordProvider,
        stt: SpeechToTextProvider,
        tts: TextToSpeechProvider,
        audio_in: AudioInputManager,
        audio_out: AudioOutputManager,
        audit: AuditLogger,
        config: VoiceSessionConfig | None = None,
    ) -> None:
        self.wake = wake
        self.stt = stt
        self.tts = tts
        self.audio_in = audio_in
        self.audio_out = audio_out
        self.audit = audit
        self.config = config or VoiceSessionConfig()
        self.active = False
        self.last_transcript = ""

    def run_once(self, respond: Callable[[str], str], click_to_talk: bool = False) -> tuple[str, str, Path | None]:
        started = time.time()
        audio = self.audio_in.capture()
        if not click_to_talk and not self.wake.detect(audio):
            return "", "", None
        transcript = self.stt.transcribe(audio, self.config.language).strip()
        self.last_transcript = transcript
        if transcript.lower() in INTERRUPT_COMMANDS:
            self.interrupt()
            return transcript, "", None
        response = respond(transcript)
        output = None
        if self.config.response_mode in {"voice_only", "text_and_voice"}:
            output = self.tts.synthesize(response, self.config.selected_voice)
            self.audio_out.enqueue(output)
            self.audio_out.play_next()
        self.audit.record(
            AuditEvent(
                action="voice.session.run_once",
                component="voice",
                params={"transcript": transcript, "response_mode": self.config.response_mode},
                started_at=started,
            )
        )
        return transcript, response, output

    def interrupt(self) -> None:
        self.stt.cancel()
        self.tts.stop()
        self.audio_out.stop()
        self.audit.record(AuditEvent(action="voice.interrupt", component="voice", params={"commands": sorted(INTERRUPT_COMMANDS)}))
