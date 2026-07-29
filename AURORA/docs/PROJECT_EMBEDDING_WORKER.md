# Worker de Embeddings de Projetos - Fase 45

Objetivo:

- Rodar indexacao semantica em ciclos controlados.
- Parar por limite de tempo, limite de lotes ou fim de pendencias.
- Gravar historico auditavel.

Comandos:

```powershell
cd D:\ISIS_IA\AURORA
python -m aurora.cli project-embed-worker --batch-size 25 --max-batches 10 --max-seconds 300
python -m aurora.cli project-embed-history --limit 20
python -m aurora.cli project-embed-progress
```

Historico:

- `D:\ISIS_IA\ISIS\logs\memory\project_embedding_worker.jsonl`

Campos principais:

- `indexed`
- `seen`
- `batches`
- `stop_reason`
- `duration_ms`
- `progress.total`
- `progress.indexed`
- `progress.pending`
- `progress.percent`

Validacao operacional:

- `project-embed-worker --batch-size 5 --max-batches 2 --max-seconds 60`: indexou 10 notas.
- Progresso apos worker: 25 de 83194 notas.
- Historico consultado por `project-embed-history`.
