# Configuracao de Voz

Campos em `data/config.json`:

- `tts_engine`: `piper`, `kokoro`, `chatterbox` ou `mock`.
- `kokoro_model_dir`, `kokoro_command`, `kokoro_voice`.
- `chatterbox_model_dir`, `chatterbox_command`, `chatterbox_voice`.
- `stt_engine`: `mock` ou `whisper_cpp`.
- `selected_voice`: voz ativa.
- `speed`, `volume`.
- `allow_interruption`.
- `use_gpu`.
- `preload_models`.
- `keep_model_loaded`.
- `audio_cache_enabled`.
- `audio_cache_max_files`.
- `strict_offline`.
- `microphone_device`, `output_device`.
- `recognition_profile`.

Comandos:

```powershell
python -m aurora.cli voice-status
python -m aurora.cli voice-test "Bom dia, Rodrigo. Estou pronta para ajudar."
python -m aurora.cli voice-cache-clear
python -m aurora.cli voice-benchmark
```

Formato de comando compativel:

```json
{
  "kokoro_command": ["python", "run_kokoro.py", "--text", "{text}", "--out", "{output}", "--voice", "{voice}"],
  "kokoro_voice": "pt-BR-feminina"
}
```

Placeholders aceitos: `{text}`, `{output}`, `{model_dir}`, `{voice}`, `{emotion}`, `{speed}`, `{volume}`.
