# Lotes de Embeddings de Projetos - Fase 44

Objetivo:

- Indexar semanticamente o cofre em lotes sem travar a maquina.
- Evitar repetir sempre as mesmas notas ja indexadas.
- Expor progresso auditavel.

Comandos:

```powershell
cd D:\ISIS_IA\AURORA
python -m aurora.cli project-embed-progress
python -m aurora.cli project-embed-batch --batch-size 50 --max-batches 4
python -m aurora.cli project-embed-worker --batch-size 25 --max-batches 10 --max-seconds 300
python -m aurora.cli project-semantic-search "ISIS memoria local" --limit 5
```

Comportamento:

- `project-embed-progress` mostra total, indexadas, pendentes e percentual.
- `project-embed-batch` executa varios lotes sequenciais.
- Cada lote seleciona apenas notas pendentes ou alteradas.
- O cofre Obsidian permanece em modo `READ_ONLY`.

Validacao operacional:

- Progresso inicial da fase: 5 de 83194 notas.
- `project-embed-batch --batch-size 5 --max-batches 2`: indexou mais 10 notas.
- Progresso final da validacao: 15 de 83194 notas.
