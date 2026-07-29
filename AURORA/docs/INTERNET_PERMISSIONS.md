# Permissoes de Internet

Modos:

- `blocked`: nenhuma requisicao externa.
- `controlled`: pesquisa publica com regras, downloads bloqueados por padrao.
- `expanded`: limites maiores, mantendo regras fixas.

Perfis:

- `CONTROLLED`: exige confirmacao para acesso externo.
- `MEDIUM`: permite pesquisa/leitura publica e pede confirmacao para acoes sensiveis.
- `TOTAL`: permite pesquisas dentro da politica, mas nao ignora regras fixas.

Comandos:

```powershell
python -m aurora.cli internet-status
python -m aurora.cli permission-summary
python -m aurora.cli permission-emergency-block
```
