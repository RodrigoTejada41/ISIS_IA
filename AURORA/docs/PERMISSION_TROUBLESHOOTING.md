# Solucao de Problemas de Permissao

## Acao bloqueada

Use:

```powershell
python -m aurora.cli permission-simulate internet.search --resource https://example.com
```

## Regra nao ativada

Regra ambigua ou de risco exige revisao/confirmacao:

```powershell
python -m aurora.cli rules-parse "texto da regra"
python -m aurora.cli rules-apply "texto da regra" --approve
```
