# Busca Hibrida - Fase 11

Servico:

```text
aurora.core.hybrid_search.HybridSearchService
```

Fontes:

- `D:\ISIS_IA\ISIS\data\databases\project_memory.sqlite`
- `D:\ISIS_IA\ISIS\data\databases\obsidian_readonly.sqlite`

Comando:

```powershell
cd D:\ISIS_IA\AURORA
python -m aurora.cli search ISIS --limit 5
```

Score inicial:

- Titulo: peso 5.
- Projeto: peso 3.
- Tags: peso 2.5.
- Categoria: peso 2.
- Links: peso 1.5.
- Checklist: bonus para consultas de tarefa/checklist.

Garantias:

- Busca local.
- Sem internet.
- Sem embeddings nesta fase.
- Auditoria de consulta.

Limitacoes:

- Nao e BM25 real.
- Nao usa vetor local.
- Conteudo completo ainda nao esta no indice de busca; usa metadados.
