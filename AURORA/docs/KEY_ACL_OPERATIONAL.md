# ACL Operacional da Chave

## Estado

- Fase 34 concluida.
- ACL restrita aplicada ao arquivo da chave.
- Heranca removida.
- `Usuarios autenticados` nao possuem mais modificacao.
- Assinatura do manifesto continua valida.

## Arquivo

- `D:\ISIS_IA\ISIS\config\report_signing_key.json`

## Backup ACL

- `D:\ISIS_IA\ISIS\config\report_signing_key_acl_20260728_213216.txt`

## ACL final

- `BUILTIN\Administradores`: controle total.
- `AUTORIDADE NT\SISTEMA`: controle total.
- `PC-TEJADA\Rodrigo Tejada`: controle total.

## Validacao

```powershell
python -m aurora.cli signature-key-acl-status
python -m aurora.cli verify-signature D:/ISIS_IA/ISIS/reports/report_integrity.json D:/ISIS_IA/ISIS/reports/report_integrity.sig.json
python -m pytest -q
```

## Observacao

Uma verificacao executada em paralelo durante a aplicacao recebeu `PermissionError`. Revalidacao serial confirmou leitura, assinatura e testes verdes.
