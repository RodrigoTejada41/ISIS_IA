# Automacao de UI

## Estado

- Fase 17 implementada em modo mock.
- Cliques reais: desativados.
- Digitacao real: desativada.
- Atalhos reais: desativados.
- Aprovacao por acao: obrigatoria.

## Componentes

- `aurora.automation.ui.UIAutomationPolicy`
- `aurora.automation.ui.UIAutomationService`
- `aurora.automation.ui.MockUIAutomationProvider`

## CLI

```powershell
python -m aurora.cli ui-plan "salvar formulario"
python -m aurora.cli ui-mock-action "salvar formulario" --approve
```

## Regras

- Toda acao planejada exige aprovacao.
- Alvos sensiveis sao bloqueados por politica.
- Valores com senha, token ou chave sao bloqueados.
- O executor atual nao interage com o Windows.

## Pendente

- Executor real com permissao temporaria.
- Janela de confirmacao por acao.
- Integracao com OCR/visao local.
- Auditoria detalhada por acao executada.
