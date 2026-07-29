# Retomada rapida

## Entrada

1. Abrir `D:\ISIS_IA\AURORA`.
2. Ler `00_MASTER.md`.
3. Ler `docs/framework/TASKS.md`.
4. Confirmar estado em `PROJECT_STATUS.md` e `SESSION_LOG.md`.

## Link da IA

- `http://127.0.0.1:8765/`

## Reiniciar HUD web

```powershell
cd D:\ISIS_IA\AURORA
python -m aurora.cli ui-hud-web --host 127.0.0.1 --port 8765
```

## Validacoes rapidas

```powershell
cd D:\ISIS_IA\AURORA
python -m py_compile aurora\ui\hud_web.py aurora\voice\local_providers.py
python -m pytest tests\test_phase48_operational_hud.py tests\test_phase47_voice_hud.py tests\test_local_voice_providers.py -q
```

## Estado esperado

- HUD web moderno em `127.0.0.1:8765`.
- Modelo de codigo: `qwen3-coder:30b`.
- Embeddings: `nomic-embed-text:latest`.
- Voz: `dii_pt-BR`.
- Microfone real: ainda desativado.

