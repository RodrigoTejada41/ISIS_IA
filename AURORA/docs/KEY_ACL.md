# ACL da Chave Local

## Estado

- Fase 32 implementada em modo somente leitura.
- Inspecao usa `icacls` quando disponivel.
- Nenhuma ACL e alterada automaticamente.

## CLI

```powershell
python -m aurora.cli signature-key-acl-status
```

## Resultado operacional atual

- Arquivo existe.
- Ha permissoes herdadas.
- `Usuarios autenticados` possuem modificacao herdada.
- Status nao e considerado restrito.

## Pendente

- Aplicar ACL restrita com backup e aprovacao explicita.
- Validar usuario dono esperado.
- Automatizar rollback de ACL.
