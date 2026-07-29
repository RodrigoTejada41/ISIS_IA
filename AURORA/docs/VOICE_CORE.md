# Voz no Nucleo - Fase 14

Factory:

```text
aurora.voice.factory.build_voice_session
```

Comando:

```powershell
cd D:\ISIS_IA\AURORA
python -m aurora.cli voice-core --transcript "corrija este codigo"
```

Resultado validado:

- STT: `mock`.
- TTS: `mock`.
- Nucleo: `IsisAssistantCore`.
- Roteamento: conectado ao provider de modelo.
- Audio mock: `D:\ISIS_IA\ISIS\data\temporary\tts_mock.wav`.

Garantias:

- Microfone real permanece desativado por padrao.
- Nenhum modelo de voz foi baixado.
- Piper e whisper.cpp so executam se caminhos forem configurados.
- Internet permanece desativada.

Limites:

- Sem captura real de microfone nesta fase.
- Sem voz Piper real nesta fase.
