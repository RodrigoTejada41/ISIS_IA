# Historico no Painel de Auditoria

## Estado

- Fase 38 implementada.
- Aba `Audit` mostra contagem de regeneracoes.
- Aba `Audit` mostra horario da ultima regeneracao.

## Campos novos

- `report_history_count`
- `last_report_generated_at`

## CLI

```powershell
python -m aurora.cli ui-audit-snapshot
```

## Pendente

- Tabela completa de historico na UI.
- Filtros por periodo.
- Botao de exportacao do historico.
