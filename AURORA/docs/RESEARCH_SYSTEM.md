# Sistema de Pesquisa

Comandos:

```powershell
python -m aurora.cli internet-test
python -m aurora.cli internet-search "pesquise documentacao Python pathlib" --approve
python -m aurora.cli internet-download "https://example.com/file.pdf" --approve
python -m aurora.cli research-history --limit 10
python -m aurora.cli internet-cache-clear
```

Resposta pesquisada inclui:

- resposta;
- fontes;
- nivel de confianca;
- limitacoes;
- data da consulta.

Pesquisa profunda:

```powershell
python -m aurora.cli internet-search "compare fontes sobre..." --mode deep --approve
```
