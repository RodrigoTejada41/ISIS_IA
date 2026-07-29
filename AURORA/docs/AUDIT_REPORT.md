# Relatorio Consolidado de Auditoria

## Estado

- Fase 28 implementada.
- Consolida acoes de UI, privilegios e memoria.
- Exporta JSON ou Markdown.
- Nao envia dados para internet.

## CLI

```powershell
python -m aurora.cli audit-report D:/ISIS_IA/ISIS/reports/audit_report.json
python -m aurora.cli audit-report D:/ISIS_IA/ISIS/reports/audit_report.md --format md
```

## Fontes

- `D:\ISIS_IA\ISIS\logs\automation\ui_actions.jsonl`
- `D:\ISIS_IA\ISIS\logs\security\privileges.jsonl`
- `D:\ISIS_IA\ISIS\logs\security\memory_approvals.jsonl`

## Pendente

- Assinatura/hash do relatorio.
- Filtros por periodo.
- Painel visual de auditoria.
