# Memoria de Projetos - Fase 9

Banco:

```text
D:\ISIS_IA\ISIS\data\databases\project_memory.sqlite
```

Fonte:

```text
D:\ISIS_IA\ISIS\brain\cerebro_vivo
```

Modo:

```text
READ_ONLY
```

Resultado da indexacao:

- Markdown escaneados: 83194.
- Criados na indexacao completa: 82194.
- Inalterados da amostra anterior: 1000.
- Tamanho do banco: 52465664 bytes.

Categorias:

- `DOCUMENTATION`: 67653.
- `BUG`: 10612.
- `TASK`: 3551.
- `DECISION`: 1080.
- `SOLUTION`: 209.
- `ARCHITECTURE`: 88.
- `REQUIREMENT`: 1.

Comandos:

```powershell
cd D:\ISIS_IA\AURORA
python -m aurora.cli index-obsidian
python -m aurora.cli project-search ISIS
```

Limitacoes:

- Busca atual e textual por metadados.
- Embeddings locais ainda nao implementados.
- Inferencia de projeto ainda e heuristica e pode gerar muitos projetos quando o cofre contem dependencias/codigo.

Proxima fase:

Fase 10: integracao Obsidian formal em modo `READ_ONLY`, com conectores de YAML, tags, links e backlinks.
