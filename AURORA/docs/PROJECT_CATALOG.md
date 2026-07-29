# Catalogo de Projetos - Fase 12

Servico:

```text
aurora.core.project_catalog.ProjectCatalog
```

Banco:

```text
D:\ISIS_IA\ISIS\data\databases\project_catalog.sqlite
```

Comandos:

```powershell
cd D:\ISIS_IA\AURORA
python -m aurora.cli consolidate-projects --min-notes 5
python -m aurora.cli projects --limit 20
```

Resultado:

- Projetos/candidatos consolidados: 29.
- Fonte: `project_memory.sqlite`.
- Sem alteracao no cofre.

Campos:

- nome
- notas
- decisoes
- bugs
- tarefas
- solucoes
- ultima modificacao
- confianca
- status

Limites:

- O catalogo ainda inclui agregadores/categorias como candidatos.
- Confirmacao manual de projetos oficiais fica para etapa posterior.
