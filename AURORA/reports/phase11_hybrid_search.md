# Fase 11 - Busca Hibrida Inicial

Banco de projetos: `D:\ISIS_IA\ISIS\data\databases\project_memory.sqlite`
Banco Obsidian: `D:\ISIS_IA\ISIS\data\databases\obsidian_readonly.sqlite`

Comando validado:

```powershell
python -m aurora.cli search ISIS --limit 5
```

Resultado:

- Busca local funcionando.
- Score auditavel por campos: titulo, projeto, categoria, tags, links e checklist.
- Resultados combinados entre memoria de projetos e metadados Obsidian.
- Nenhum embedding ou servico externo usado.

Limitacoes:

- Ainda nao usa BM25 real nem vetor local.
- Busca por conteudo completo ainda nao foi indexada; foco atual e metadados.
- Inferencia de projeto ainda precisa refinamento.

Proxima fase:

Fase 12 - memoria de projetos dedicada e consolidacao de projetos reais.
