__all__ = [
    "ConfiguredWakeWordProvider",
    "build_voice_session",
    "MockSpeechToTextProvider",
    "MockTextToSpeechProvider",
    "MockWakeWordProvider",
    "PiperTextToSpeechProvider",
    "VoiceSessionManager",
    "WhisperCppSpeechToTextProvider",
]


def __getattr__(name: str):
    if name == "build_voice_session":
        from .factory import build_voice_session

        return build_voice_session
    if name in {"ConfiguredWakeWordProvider", "PiperTextToSpeechProvider", "WhisperCppSpeechToTextProvider"}:
        from .local_providers import ConfiguredWakeWordProvider, PiperTextToSpeechProvider, WhisperCppSpeechToTextProvider

        return {
            "ConfiguredWakeWordProvider": ConfiguredWakeWordProvider,
            "PiperTextToSpeechProvider": PiperTextToSpeechProvider,
            "WhisperCppSpeechToTextProvider": WhisperCppSpeechToTextProvider,
        }[name]
    if name in {"MockSpeechToTextProvider", "MockTextToSpeechProvider", "MockWakeWordProvider"}:
        from .providers import MockSpeechToTextProvider, MockTextToSpeechProvider, MockWakeWordProvider

        return {
            "MockSpeechToTextProvider": MockSpeechToTextProvider,
            "MockTextToSpeechProvider": MockTextToSpeechProvider,
            "MockWakeWordProvider": MockWakeWordProvider,
        }[name]
    if name == "VoiceSessionManager":
        from .session import VoiceSessionManager

        return VoiceSessionManager
    raise AttributeError(name)
