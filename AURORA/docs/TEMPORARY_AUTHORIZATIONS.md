# Autorizacoes Temporarias

Criar:

```powershell
python -m aurora.cli permission-temp-add internet.search --resource github.com --minutes 60 --max-uses 5
```

Simular:

```powershell
python -m aurora.cli permission-simulate internet.search --resource github.com
```

Autorizacoes expiradas deixam de valer automaticamente.
