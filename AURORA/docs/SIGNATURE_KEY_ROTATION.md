# Rotacao da Chave de Assinatura

## Estado

- Fase 31 implementada.
- Rotacao cria backup antes de gerar nova chave.
- Status mostra `key_id`, tamanho, backups e flag de somente leitura.
- Chave antiga nao e apagada automaticamente.

## CLI

```powershell
python -m aurora.cli signature-key-status
python -m aurora.cli signature-key-rotate
```

## Regras

- Backup fica ao lado da chave.
- Nova chave invalida assinaturas antigas para verificacao ativa.
- Assinaturas antigas podem ser verificadas apenas com backup restaurado.

## Pendente

- ACL restrita por usuario no Windows.
- Rotacao autenticada.
- Politica de retencao de backups.
