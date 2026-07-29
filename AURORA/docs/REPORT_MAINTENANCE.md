# Manutencao de Relatorios

## Estado

- Fase 36 implementada.
- Regenera relatorio de auditoria.
- Regenera manifesto de integridade.
- Assina novamente o manifesto.
- Verifica assinatura ao final.

## CLI

```powershell
python -m aurora.cli reports-regenerate
```

## UI

- Aba `Audit`.
- Botao `Regenerate reports`.

## Ordem

1. `audit_report.json`
2. `report_integrity.json`
3. `report_integrity.sig.json`
4. verificacao da assinatura

## Pendente

- Historico de execucoes.
- Agendamento local.
- Relatorio incremental por periodo.
