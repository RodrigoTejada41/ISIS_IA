# Diagnostico de Voz

## Sem audio

1. Execute `python -m aurora.cli voice-status`.
2. Verifique `piper_binary_exists` e `piper_voice_exists`.
3. Execute `python -m aurora.cli voice-test`.
4. Se `audio_path` existir, o problema e reproducao, nao sintese.

## Motor Kokoro/Chatterbox indisponivel

Comportamento esperado enquanto nao houver pacote/modelo local validado. O roteador registra fallback e usa Piper.

## Microfone

STT server-side real ainda exige `whisper_cpp` configurado. No HUD web, `MIC` usa Web Speech Recognition do navegador.

## Cache

Limpar:

```powershell
python -m aurora.cli voice-cache-clear
```

