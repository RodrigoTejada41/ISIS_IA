# Auditoria de Acoes

## Estado

- Fase 19 implementada.
- Log JSONL local: `D:\ISIS_IA\ISIS\logs\automation\ui_actions.jsonl`.
- Execucao real de UI: desativada.
- Auditoria registra tambem acoes bloqueadas.

## CLI

```powershell
python -m aurora.cli ui-permissions-status
python -m aurora.cli ui-action-audit --limit 20
```

## Registro

Campos gravados:

- `status`
- `action_type`
- `target`
- `reason`
- `approved`
- `real_execution`
- `created_at`

## Pendente

- Tela local de permissoes.
- Identificador de sessao por acao.
- Hash de contexto visual.
- Exportacao de relatorio.
