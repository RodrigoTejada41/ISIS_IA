# Voz Real com Piper - Fase 47

Estado:

- TTS real ativo com Piper.
- STT continua `mock`.
- Microfone real continua desativado por politica.
- HUD mostra status de voz e possui botao `VOZ TESTE`.

Runtime:

- `D:\ISIS_IA\ISIS\runtime\piper\piper\piper.exe`

Voz:

- `D:\ISIS_IA\ISIS\voice\piper\voices\pt_BR-faber-medium\pt\pt_BR\faber\medium\pt_BR-faber-medium.onnx`

Comandos:

```powershell
cd D:\ISIS_IA\AURORA
python -m aurora.cli voice-status
python -m aurora.cli voice-speak "ISIS voz real local ativa."
python -m aurora.cli voice-speak "ISIS voz real local ativa." --play
python -m aurora.cli voice-core --transcript "corrija este codigo Python: print('oi')"
python -m aurora.cli ui-hud
```

Validacao operacional:

- `voice-status`: Piper e voz existem.
- `voice-speak`: gerou WAV real em `D:\ISIS_IA\ISIS\data\temporary`.
- `voice-core --transcript "status"` gerou resposta em WAV com engine `piper`.

Limites:

- Entrada por microfone real ainda nao foi ativada.
- Reconhecimento de voz real ainda depende de instalar/configurar `whisper.cpp`.
- Comandos bloqueados por politica geram resposta falada informando bloqueio.
