# Interface HUD - Fase 46

Objetivo:

- Criar interface visual premium estilo central de comando IA.
- Manter runtime leve em Tkinter.
- Nao alterar politicas de seguranca.

Comandos:

```powershell
cd D:\ISIS_IA\AURORA
python -m aurora.cli ui-hud-snapshot
python -m aurora.cli ui-hud
python -m aurora.cli ui-hud-web
```

Link local:

```text
http://127.0.0.1:8765/
```

Layout:

- Barra superior com nome, perfil, RAM, VRAM, internet, microfone e modo.
- Navegacao lateral: conversa, memoria, projetos, documentos, automacoes, agenda e configuracoes.
- Centro com canal principal de conversa.
- Painel direito com nucleo IA, modelo de codigo, embeddings, notas e status offline.
- Rodape com campo de comando e acoes de microfone/anexo/envio/parada.
- Rodape com botao `VOZ LOCAL` para validar Piper local.
- Campo de comando envia prompts reais para `IsisAssistantCore`.
- Respostas aparecem no historico da conversa.
- Respostas geram audio Piper quando TTS esta pronto.
- Versao web local exposta por `ui-hud-web`.
- Avatar animado em Canvas com aneis, pulso e linhas de energia.

Status real exibido:

- Modelo de codigo: `qwen3-coder:30b`.
- Modelo de embeddings: `nomic-embed-text:latest`.
- Notas indexadas: `83194`.
- Embeddings de projetos: indexadas e pendentes.
- Perfil: `MEDIUM`.
- Offline: ativo.
- Voz: Piper local quando configurado.

Validacao:

- `ui-hud-snapshot` retorna JSON operacional.
- `ui-hud-web` expõe `/`, `/api/snapshot`, `/api/chat`, `/api/voice-test` e `/api/audio`.
- Testes focados da Fase 46: 2 passed.
- Testes focados da Fase 48: 7 passed.

## Melhoria web mic/voz/navegacao

- `MIC` usa Web Speech Recognition do navegador em `pt-BR`.
- `VOZ LOCAL` usa o WAV gerado pelo Piper local. A voz TTS do Windows/Chrome nao e usada para responder.
- Navegacao lateral alterna paineis reais de memoria, projetos, documentos, automacoes, agenda e configuracoes.
- `ANEXO` abre seletor local de arquivos e registra nomes no historico.
- `PARAR` cancela voz web, ditado e resposta pendente no cliente.
- Validacao focada: `python -m pytest tests\test_phase48_operational_hud.py -q` com 3 passed.
