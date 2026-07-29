# Ponte Tela e Automacao

## Estado

- Fase 18 implementada em modo mock.
- OCR real: nao implementado.
- Execucao real de UI: desativada.
- Baixa confianca: bloqueada.
- Aprovacao por acao: obrigatoria.

## Componentes

- `aurora.automation.screen_bridge.ScreenAutomationBridge`
- `aurora.automation.screen_bridge.ScreenActionSuggestion`

## CLI

```powershell
python -m aurora.cli screen-ui-suggest "salvar" --text "Botao salvar" --approve
```

## Fluxo

1. Recebe texto mock da tela.
2. Analisa campos e botoes.
3. Sugere uma acao de UI.
4. Bloqueia baixa confianca.
5. Executa somente em mock quando aprovado.

## Pendente

- OCR local.
- Coordenadas reais dos elementos.
- Validacao visual por modelo local.
- Execucao real temporaria com auditoria.
