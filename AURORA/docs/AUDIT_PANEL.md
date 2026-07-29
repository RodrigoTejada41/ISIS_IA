# Painel de Auditoria

## Estado

- Fase 35 implementada.
- Dashboard possui aba `Audit`.
- Snapshot CLI disponivel.
- Exibe contadores de eventos, integridade de relatorios e ACL da chave.

## CLI

```powershell
python -m aurora.cli ui-audit-snapshot
python -m aurora.cli ui-dashboard
```

## Campos

- `ui_actions`
- `privilege_events`
- `memory_events`
- `report_integrity_ok`
- `signature_key_restricted`
- `reports_root`

## Pendente

- Lista detalhada filtravel dos eventos.
- Indicadores visuais de alerta.
- Botao para regenerar relatorios.
