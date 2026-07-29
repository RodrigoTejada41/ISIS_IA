# Embeddings de Memoria - Fase 40

Banco:

- `D:\ISIS_IA\ISIS\data\databases\memory_embeddings.sqlite`

Modelo:

- `nomic-embed-text:latest`
- Provider: Ollama local em `D:\ISIS_IA\ISIS\runtime\ollama`
- Modelos em `D:\ISIS_IA\ISIS\models\ollama`

Comandos:

```powershell
cd D:\ISIS_IA\AURORA
.\scripts\start_ollama_project.ps1
python -m aurora.cli memory-embed --limit 100
python -m aurora.cli memory-semantic-search "embeddings locais no ssd" --limit 5
```

Escopo:

- Indexa `memory_records` confirmadas.
- Ignora memorias com sensibilidade `HIGH`.
- Usa SHA-256 do conteudo para evitar reindexacao desnecessaria.
- Nao altera o cofre Obsidian.

Validacao operacional:

- `memory-embed --limit 10`: `indexed=2`.
- Segunda execucao: `skipped=2`.
- `memory-semantic-search "embeddings locais no ssd"` retornou a memoria correta em primeiro lugar.
