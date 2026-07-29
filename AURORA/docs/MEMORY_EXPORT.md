# Exportacao de Memoria

## Estado

- Fase 27 implementada.
- UI possui filtro por status na aba `Memory`.
- Exportacao local em JSON ou Markdown.
- Exportacao nao altera Obsidian.

## CLI

```powershell
python -m aurora.cli ui-memory-export D:/ISIS_IA/ISIS/reports/memory_report.json --status CONFIRMED
python -m aurora.cli ui-memory-export D:/ISIS_IA/ISIS/reports/memory_report.md --format md
```

## Regras

- Formatos aceitos: `json`, `md`.
- Exportacao respeita filtro de status.
- Conteudo sensivel alto segue oculto por padrao.

## Pendente

- Exportacao por periodo.
- Exportacao com assinatura/hash.
- Relatorio consolidado de auditoria.
