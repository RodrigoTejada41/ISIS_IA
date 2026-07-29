# Fase 13 - Decisoes e Bugs

Banco:

```text
D:\ISIS_IA\ISIS\data\databases\knowledge_records.sqlite
```

Comandos executados:

```powershell
python -m aurora.cli import-knowledge-records
python -m aurora.cli decisions ISIS
python -m aurora.cli bugs ISIS
```

Resultado:

- Decisoes importadas: 1080.
- Bugs importados: 10612.
- IDs estaveis por UUIDv5 a partir de categoria e caminho.
- Importacao idempotente.
- Fonte: `project_memory.sqlite`.
- Cofre Obsidian mantido em `READ_ONLY`.

Limitacao:

Os registros sao importados por heuristica de categoria. Devem ser revisados/refinados antes de virar base oficial final.

Proxima fase:

Fase 14 - voz local conectada ao nucleo, ainda com providers mock/configuraveis ate autorizacao de modelos reais.
