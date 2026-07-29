# Aplicacao Controlada de ACL

## Estado

- Fase 33 implementada.
- Aplicacao exige `--apply`.
- Sem `--apply`, o comando e apenas dry-run.
- Antes de aplicar, cria backup ACL via `icacls /save`.
- Rollback usa `icacls /restore`.

## CLI

```powershell
python -m aurora.cli signature-key-acl-apply
python -m aurora.cli signature-key-acl-apply --apply
python -m aurora.cli signature-key-acl-rollback <backup_acl.txt> --apply
```

## Regras

- Remove heranca com `/inheritance:r`.
- Concede acesso total ao usuario atual.
- Concede acesso total a `SYSTEM`.
- Concede acesso total a `Administrators` via SID.

## Pendente

- Executar aplicacao operacional apos revisar dry-run.
- Guardar ultimo backup ACL em estado consultavel.
- Botao visual no dashboard.
