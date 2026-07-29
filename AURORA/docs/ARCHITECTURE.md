# Arquitetura

Camadas:

- `aurora.core`: regras de negocio, auditoria, permissoes, recursos, memoria e roteamento.
- `aurora.voice`: contratos de wake word, STT, TTS, entrada e saida de audio.
- `aurora.skills`: manifestos, sandbox, instalacao aprovada e rollback.
- `aurora.cli`: entrada operacional local para automacao e testes manuais.
- `aurora.core.runtime`: composicao de configuracao, auditoria, memoria, permissoes, recursos, roteador e habilidades.
- `aurora.core.assistant`: nucleo ISIS com inicializacao, eventos, comandos, ferramentas, health check e shutdown.
- `data/skills`: habilidades locais isoladas.
- `data/config.json`: configuracao local gerada automaticamente.
- `tests`: validacao automatizada com mocks.

Principios aplicados:

- UI nao implementada nesta etapa; o nucleo expoe estado suficiente para uma UI futura.
- Integracoes externas sao adaptadores, nao dependencias obrigatorias.
- Acoes destrutivas nao existem nas habilidades iniciais.
- Auditoria sanitiza segredos.
- Recursos sao checados antes da escolha do modelo.
- CLI retorna JSON e nao executa servicos online automaticamente.
