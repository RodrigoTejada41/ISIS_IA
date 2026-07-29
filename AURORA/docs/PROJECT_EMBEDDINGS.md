# Embeddings de Projetos - Fase 43

Banco:

- `D:\ISIS_IA\ISIS\data\databases\project_note_embeddings.sqlite`

Fonte:

- `D:\ISIS_IA\ISIS\data\databases\project_memory.sqlite`
- Arquivos Markdown em `D:\ISIS_IA\ISIS\brain\cerebro_vivo`

Modelo:

- `nomic-embed-text:latest`
- Runtime: Ollama local em `D:\ISIS_IA\ISIS\runtime\ollama`

Comandos:

```powershell
cd D:\ISIS_IA\AURORA
.\scripts\start_ollama_project.ps1
python -m aurora.cli project-embed --limit 50
python -m aurora.cli project-embed-progress
python -m aurora.cli project-embed-batch --batch-size 50 --max-batches 4
python -m aurora.cli project-embed --project ISIS --limit 100
python -m aurora.cli project-semantic-search "ISIS memoria local" --limit 5
```

Escopo:

- Leitura somente leitura dos arquivos Markdown.
- Indexacao em lotes por `--limit`.
- `project-embed` seleciona notas pendentes ou alteradas.
- `project-embed-progress` mostra total/indexadas/pendentes.
- Filtros opcionais por `--project` e `--category`.
- Reindexacao idempotente por `content_hash` do `project_memory.sqlite`.
- Nao altera o cofre Obsidian.

Validacao operacional:

- `project-embed --limit 5`: `indexed=5`.
- `project-semantic-search "ISIS memoria local"` retornou resultados do cofre indexado.
