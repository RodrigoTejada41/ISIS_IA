# Decisoes e Bugs - Fase 13

Store:

```text
aurora.core.knowledge_records.KnowledgeRecordStore
```

Banco:

```text
D:\ISIS_IA\ISIS\data\databases\knowledge_records.sqlite
```

Comandos:

```powershell
cd D:\ISIS_IA\AURORA
python -m aurora.cli import-knowledge-records
python -m aurora.cli decisions ISIS
python -m aurora.cli bugs ISIS
```

Resultado:

- Decisoes importadas: 1080.
- Bugs importados: 10612.
- Importacao idempotente.
- IDs estaveis por UUIDv5.

Campos de decisao:

- id
- projeto
- descricao
- contexto
- arquivo origem
- versao
- status
- data

Campos de bug:

- id
- projeto
- titulo
- descricao
- arquivo origem
- status
- prioridade
- versao
- data

Limite:

Classificacao ainda e heuristica. Registros importados exigem revisao antes de serem considerados definitivos.
