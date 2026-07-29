# Modelos

O codigo nao fixa nomes comerciais.

Cada modelo local deve informar:

- `model_id`
- perfis suportados
- memoria estimada
- contexto maximo
- prioridade
- status habilitado

Hardware alvo:

- CPU: AMD Ryzen 7 5700.
- RAM: 32 GB.
- GPU: NVIDIA RTX 3060 12 GB VRAM.
- Limite padrao de VRAM: 10 GB.
- Modelos grandes nao devem ficar carregados simultaneamente sem necessidade.

## Fase 8

Camada local implementada em `aurora.core.model_provider`.

Providers:

- Mock.
- Ollama local.
- llama.cpp local.
- LM Studio local.

Estado:

- Ollama encontrado no PATH.
- `ollama list` nao retornou modelos instalados.
- `nvidia-smi` encontrou RTX 3060 com 12288 MB totais.
