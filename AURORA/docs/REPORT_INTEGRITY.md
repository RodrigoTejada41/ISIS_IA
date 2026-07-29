# Integridade de Relatorios

## Estado

- Fase 29 implementada.
- Manifesto local com SHA-256.
- Verificacao detecta arquivo ausente ou alterado.
- Sem chave secreta e sem rede.

## CLI

```powershell
python -m aurora.cli report-integrity D:/ISIS_IA/ISIS/reports/report_integrity.json
python -m aurora.cli report-integrity-verify D:/ISIS_IA/ISIS/reports/report_integrity.json
```

## Regras

- Hash: SHA-256.
- Manifesto ignora o proprio arquivo de saida.
- Verificacao falha se algum arquivo mudou.

## Pendente

- Assinatura com chave local.
- Rotacao de manifestos.
- Integracao visual no dashboard.
