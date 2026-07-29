# Visao de Tela

## Estado

- Fase 16 implementada em modo manual/mock.
- Captura real de tela: desativada.
- Captura continua: desativada.
- Armazenamento de imagens: desativado.
- Redacao de dados sensiveis: ativa.

## Componentes

- `aurora.perception.screen.ScreenPrivacyPolicy`
- `aurora.perception.screen.MockScreenProvider`
- `aurora.perception.screen.ScreenAnalyzer`
- `aurora.perception.screen.ScreenVisionService`

## CLI

```powershell
python -m aurora.cli screen-status
python -m aurora.cli screen-mock --text "Campo login`nBotao entrar"
```

## Regras

- Nenhuma captura real ocorre sem comando explicito futuro.
- O modo atual exige confirmacao manual.
- Aplicativos sensiveis sao bloqueados por nome.
- Senhas, tokens, CPF e cartoes sao mascarados antes do retorno.

## Pendente

- Captura real sob aprovacao explicita.
- OCR local.
- Analise visual por modelo local.
- UI de permissao temporaria.
