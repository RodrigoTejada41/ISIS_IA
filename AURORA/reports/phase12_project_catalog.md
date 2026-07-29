# Fase 12 - Memoria de Projetos Consolidada

Banco:

```text
D:\ISIS_IA\ISIS\data\databases\project_catalog.sqlite
```

Comando executado:

```powershell
python -m aurora.cli consolidate-projects --min-notes 5
python -m aurora.cli projects --limit 20
```

Resultado:

- Projetos/candidatos consolidados: 29.
- Banco criado: `project_catalog.sqlite`.
- Fonte: `project_memory.sqlite`.
- Escrita apenas em banco da ISIS.
- Cofre Obsidian mantido em `READ_ONLY`.

Observacao tecnica:

A consolidacao ainda classifica alguns agregadores do cofre como candidatos de projeto, por exemplo `projetos`, `historico`, `Logs` e categorias semelhantes. Eles permanecem no catalogo como candidatos com confianca calculada, nao como confirmacao manual definitiva.

Proxima fase:

Fase 13 - registros formais de decisoes e bugs.
