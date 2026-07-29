# AURORA

Assistente local offline-first para Windows, com voz mockada para testes, roteamento automatico de modelos, memoria local, permissoes e habilidades versionadas.

## Estado

- Projeto criado neste workspace porque nao havia pasta AURORA, `README.md`, `docs/` ou testes existentes em `D:\ISIS_IA`.
- Baseline antes das alteracoes: `python -m pytest` em `D:\ISIS_IA` coletou 0 testes.
- Validacao atual: `python -m pytest` em `D:\ISIS_IA\AURORA`.

## Comandos

```powershell
cd D:\ISIS_IA\AURORA
python -m pytest
python -m aurora.cli status
python -m aurora.cli route "corrija este codigo"
python -m aurora.cli voice-mock --transcript "qual o status"
```

## Dependencias

| Dependencia | Obrigatoria | Uso | Observacao |
|---|---:|---|---|
| Python 3.11+ | Sim | runtime e testes | Validado com Python 3.12 |
| pydantic | Sim | validacao de manifestos de habilidades | ja disponivel no ambiente |
| psutil | Nao | RAM real | fallback interno quando ausente |
| nvidia-smi | Nao | VRAM NVIDIA real | fallback assume RTX 3060 12 GB com margem |
| whisper.cpp | Nao | STT real | nao baixa modelo automaticamente |
| Piper | Nao | TTS local | usar voz pt-BR feminina instalada |
| openWakeWord | Nao | palavra de ativacao real | mock em testes |
| Ollama | Nao | modelos locais e embeddings | online desativado por padrao |
| Qdrant | Nao | vetor local futuro | SQLite textual e fallback atual |

## Instalar modelos de voz

1. Baixe manualmente modelo Piper pt-BR feminino de fonte confiavel.
2. Configure o caminho no futuro adaptador `TextToSpeechProvider`.
3. Nao use clonagem de voz real sem autorizacao documentada.

## Instalar modelos de reconhecimento

1. Instale `whisper.cpp`.
2. Baixe manualmente modelos `tiny`, `base`, `small` ou `medium`.
3. Configure idioma padrao `pt-BR`.
4. Nao ha download automatico sem aprovacao.

## Configurar perfis de modelos

Registre `ModelSpec` com `model_id`, perfis (`GENERAL`, `FAST`, `CODING`, etc.) e memoria estimada. O roteador nao fixa nomes comerciais.

## CLI

Consulte [docs/CLI.md](docs/CLI.md).

## Configuracao

Consulte [docs/CONFIGURATION.md](docs/CONFIGURATION.md).
