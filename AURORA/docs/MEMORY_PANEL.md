# Painel de Memoria

## Estado

- Fase 25 implementada.
- Memoria editavel usa SQLite local da AURORA.
- Obsidian permanece `READ_ONLY`.
- Registros novos entram como `PROPOSED`.
- Confirmacao/rejeicao altera apenas status local.

## CLI

```powershell
python -m aurora.cli ui-memory-propose "registrar decisao local"
python -m aurora.cli ui-memory-list --status PROPOSED
python -m aurora.cli ui-memory-status <id> CONFIRMED
```

## Regras

- Conteudo vazio e rejeitado.
- Status deve ser valido.
- Busca RAG usa somente registros `CONFIRMED`.
- Dados sensiveis altos nao aparecem por padrao.

## Pendente

- Botoes de confirmar/rejeitar direto na UI.
- Formulario completo com projeto/tags.
- Auditoria especifica de aprovacao de memoria.
