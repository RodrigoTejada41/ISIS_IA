# Historico de Regeneracao de Relatorios

## Estado

- Fase 37 implementada.
- Cada execucao de `reports-regenerate` grava um evento JSONL.
- Historico fica local.

## CLI

```powershell
python -m aurora.cli reports-history --limit 20
```

## Arquivo

- `D:\ISIS_IA\ISIS\logs\security\report_maintenance.jsonl`

## Campos

- `created_at`
- `ok`
- `audit_report`
- `integrity_manifest`
- `signature`
- `signature_ok`

## Pendente

- Exibir historico na aba `Audit`.
- Limpeza/retencao de historico.
- Filtro por periodo.
