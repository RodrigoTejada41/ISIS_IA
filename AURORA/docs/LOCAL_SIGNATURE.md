# Assinatura Local de Relatorios

## Estado

- Fase 30 implementada.
- Assinatura: HMAC-SHA256.
- Chave local: `D:\ISIS_IA\ISIS\config\report_signing_key.json`.
- Sem envio externo.

## CLI

```powershell
python -m aurora.cli signature-key-status
python -m aurora.cli sign-report D:/ISIS_IA/ISIS/reports/report_integrity.json D:/ISIS_IA/ISIS/reports/report_integrity.sig.json
python -m aurora.cli verify-signature D:/ISIS_IA/ISIS/reports/report_integrity.json D:/ISIS_IA/ISIS/reports/report_integrity.sig.json
```

## Regras

- A chave e criada automaticamente se nao existir.
- A assinatura falha se o arquivo mudar.
- O arquivo da chave nao deve ser publicado.

## Pendente

- Permissao restrita no arquivo de chave no Windows.
- Rotacao de chave.
- Exportacao com cadeia de confianca.
