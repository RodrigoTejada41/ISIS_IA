# Solucao de Problemas de Internet

## Internet bloqueada

Verificar:

```powershell
python -m aurora.cli internet-status
python -m aurora.cli permission-summary
```

## Pesquisa pede confirmacao

Use:

```powershell
python -m aurora.cli internet-search "consulta" --approve
```

## Bloqueio SSRF

Enderecos locais, privados e portas nao autorizadas sao bloqueados por politica.
