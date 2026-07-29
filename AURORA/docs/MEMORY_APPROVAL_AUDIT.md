# Auditoria de Aprovacao de Memoria

## Estado

- Fase 26 implementada.
- Log JSONL: `D:\ISIS_IA\ISIS\logs\security\memory_approvals.jsonl`.
- Propostas, confirmacoes e rejeicoes sao auditadas.
- UI local tem botoes `Confirm` e `Reject`.
- Obsidian permanece `READ_ONLY`.

## CLI

```powershell
python -m aurora.cli memory-approval-audit --limit 20
```

## Regras

- Conteudo vazio gera auditoria de falha.
- Confirmacao muda status para `CONFIRMED`.
- Rejeicao muda status para `REJECTED`.
- Busca RAG segue usando apenas `CONFIRMED`.

## Pendente

- Campo de motivo manual para aprovar/rejeitar.
- Filtro visual por status na UI.
- Exportacao de relatorio.
