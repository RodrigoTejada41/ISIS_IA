# Voz

Contratos implementados:

- `WakeWordProvider`
- `SpeechToTextProvider`
- `TextToSpeechProvider`
- `AudioInputManager`
- `AudioOutputManager`
- `VoiceSessionManager`

Fluxo validado por mock:

1. Captura audio.
2. Detecta palavra `aurora`.
3. Transcreve texto.
4. Envia para callback de resposta.
5. Sintetiza audio mock.
6. Enfileira e reproduz.
7. Interrompe por comando local: `pare`, `cancelar`, `silencio`, `silêncio`, `interromper`.

Pendencias de integracao real:

- Captura real de microfone.
- Selecao real de dispositivos.
- Prevencao fisica de eco.

Adaptadores preparados:

- `WhisperCppSpeechToTextProvider`: exige binario e modelo ja existentes.
- `PiperTextToSpeechProvider`: exige binario Piper e voz ja existentes.
- `ConfiguredWakeWordProvider`: palavra configuravel e modo desativado.

## Fase 14

Voz conectada ao nucleo via `build_voice_session`.

CLI:

```powershell
python -m aurora.cli voice-core --transcript "status"
```
