# Instalacao de Voz Local

## Atual

Piper ja esta configurado em `data/config.json`.

Validar:

```powershell
python -m aurora.cli voice-status
python -m aurora.cli voice-test --play
```

## Whisper local

Configure `voice.stt_engine=whisper_cpp`, `voice.stt_binary_path` e `voice.stt_model_path` em `data/config.json`.

Modelos devem ficar fora do executavel, preferencialmente em `D:\ISIS_IA\ISIS\models`.

## Kokoro/Chatterbox

Kokoro e Chatterbox sao compativeis por adaptador CLI local.

Opcoes:

- configurar `voice.kokoro_command` ou `voice.chatterbox_command` em `data/config.json`;
- ou criar `tts_manifest.json` dentro de `voice.kokoro_model_dir` ou `voice.chatterbox_model_dir`.

Exemplo de manifesto:

```json
{
  "voice": "pt-BR-feminina",
  "command": ["python", "run_tts.py", "--text", "{text}", "--out", "{output}", "--voice", "{voice}"]
}
```

O comando deve gerar um WAV no caminho recebido em `{output}`. A licenca do modelo local continua responsabilidade da instalacao.
