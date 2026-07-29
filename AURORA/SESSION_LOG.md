# Registro de Sessao

## 2026-07-28

Problemas identificados antes da correcao:

- Projeto AURORA nao estava presente no workspace.
- Documentacao obrigatoria solicitada nao existia.
- Testes atuais inexistentes.
- Requisitos dos anexos sao amplos demais para uma unica etapa com integracoes reais sem dependencias instaladas.

Alteracoes:

- Criada base Python modular.
- Criados testes com mocks.
- Criada documentacao tecnica inicial.
- Criadas habilidades seguras locais.

Validacao:

- `python -m pytest` em `D:\ISIS_IA\AURORA`: 19 passed.

## 2026-07-28 - continuidade

Problemas identificados:

- Faltava entrada operacional para executar o nucleo fora dos testes.
- Faltava persistencia de configuracao.
- Integracoes reais de voz nao tinham adaptadores executaveis configuraveis.

Alteracoes:

- Criado `AuroraRuntime`.
- Criado `ConfigStore` e `AuroraConfig`.
- Criada CLI local.
- Criados adaptadores `WhisperCppSpeechToTextProvider`, `PiperTextToSpeechProvider` e `ConfiguredWakeWordProvider`.
- Criados testes adicionais.

Validacao:

- `python -m pytest` em `D:\ISIS_IA\AURORA`: 29 passed.

## 2026-07-28 - Fase 1 ISIS

Problemas identificados:

- Prompt novo exige executar somente auditoria antes de migracao.
- Busca ampla por todos os drives atingiu timeout, mas encontrou `E:\Projetos\CEREBRO_VIVO`.
- Auditoria Python completa do cofre excedeu 120s.

Correcoes:

- Criado auditor com limites de tempo/arquivos.
- Ignorados diretorios tecnicos na analise de conteudo.
- Complementados totais com `robocopy /L`, sem copiar arquivos.

Evidencias:

- `reports/phase1_audit.md`
- `reports/phase1_audit.json`
- `reports/phase1_robocopy_totals.txt`

Resultado:

- Fase 1 executada em modo somente leitura.
- Nenhum arquivo do CEREBRO VIVO foi movido, apagado ou modificado.

## 2026-07-28 - Fase 2 ISIS

Problemas identificados:

- Era necessario criar estrutura de destino sem iniciar migracao.
- O script precisava ser idempotente para permitir repeticao segura.

Alteracoes:

- Criado `scripts/phase2_create_ssd_structure.py`.
- Criado `D:\ISIS_IA\ISIS`.
- Criados 46 diretorios.
- Criado manifesto em `D:\ISIS_IA\ISIS\config\phase2_structure_manifest.json`.
- Criado relatorio `reports/phase2_structure.md`.

Validacao:

- `python -m pytest`: 32 passed.

Resultado:

- Fase 2 concluida.
- CEREBRO VIVO original permaneceu intacto.

## 2026-07-28 - Fase 3 ISIS

Problemas identificados:

- Backup precisa preservar origem e nao usar espelhamento destrutivo.
- `robocopy` retorna codigo 1 quando copia arquivos com sucesso.

Alteracoes:

- Criado `scripts/phase3_backup_cerebro_vivo.py`.
- Backup criado em `D:\ISIS_IA\ISIS\backups\manual\cerebro_vivo_backup_20260728_153131`.
- Criado manifesto `backup_manifest.json`.
- Criado log `D:\ISIS_IA\ISIS\logs\migration\phase3_backup_20260728_153131.log`.
- Criado `docs/BACKUP.md`.

Validacao:

- Origem: 203112 arquivos, 5286560147 bytes.
- Destino: 203112 arquivos, 5286560147 bytes.
- `robocopy` exit code: 1, tratado como sucesso.

Resultado:

- Fase 3 concluida por contagem/tamanho.
- Hash completo ainda pendente antes da migracao.

## 2026-07-28 - Fase 4 ISIS

Problemas identificados:

- Migracao precisava abortar se destino tivesse arquivos.
- Validacao deveria ignorar manifestos gerados e comparar origem/destino por hash.
- Backup contem arquivo extra `backup_manifest.json`, entao nao deve ser usado como par exato de comparacao.

Alteracoes:

- Criado `scripts/phase4_migrate_cerebro_vivo.py`.
- Cofre copiado para `D:\ISIS_IA\ISIS\brain\cerebro_vivo`.
- Criado manifesto completo em `D:\ISIS_IA\ISIS\logs\migration\migration_manifest.json`.
- Criado relatorio `reports/phase4_migration.md`.
- Criado `docs/MIGRATION.md`.

Validacao:

- Origem: 203112 arquivos, 5286560147 bytes.
- Destino: 203112 arquivos, 5286560147 bytes.
- SHA-256 comparados: 203112.
- Ausentes: 0.
- Extras: 0.
- Alterados: 0.

Resultado:

- Fase 4 concluida.
- CEREBRO VIVO original preservado.
- Obsidian ainda nao foi apontado para o novo local.

## 2026-07-28 - Fase 5 ISIS

Problemas identificados:

- Obsidian estava aberto durante a sessao; testes unitarios nao devem depender desse estado.
- Validador inicial tratava links de pasta relativa como ausentes.
- Cofre possui links internos nao resolvidos na amostra.

Correcoes:

- Testes de backup/migracao usam `allow_open_obsidian=True` apenas nos cenarios fake.
- Validador aceita pasta, caminho relativo e variante `.md`.
- Links restantes foram registrados como pendencia, sem alterar notas.

Validacao:

- Cofre migrado existe.
- `.obsidian` existe.
- Manifesto de migracao validado.
- 2601 anexos, 0 vazios.
- 170934 links verificados em 5000 Markdown.
- 200 links nao resolvidos na amostra.

Resultado:

- Fase 5 concluida com status `warning`.
- Integridade da migracao permanece valida.
- Pendencia: saneamento manual/controlado de links internos.

## 2026-07-28 - Correcao de riscos e Fase 6 ISIS

Problemas identificados:

- Links restantes nao poderiam ser corrigidos sem alvo comprovavel.
- Scripts de Fase 5/6 falhavam quando executados diretamente por problema de import.
- Configuracao central ainda nao existia no SSD da ISIS.

Correcoes:

- Criado `scripts/phase5_remediate_links.py`.
- Corrigidos 87 links com alvo existente.
- Criado backup dos arquivos alterados.
- Corrigido `sys.path` em scripts executaveis.
- Criado `scripts/phase6_configure_isis.py`.
- Criado `D:\ISIS_IA\ISIS\config\isis_config.json`.
- Atualizado `D:\ISIS_IA\AURORA\data\config.json`.

Validacao:

- Testes focados: 9 passed.
- Fase 6 executada com status `configured`.

Resultado:

- Fase 6 concluida.
- Cofre configurado em `READ_ONLY`.
- Risco residual: links sem alvo comprovavel continuam como `warning`.

## 2026-07-28 - Fase 7 ISIS

Problemas identificados:

- Nao havia nucleo central para inicializacao/comandos/shutdown.
- CLI falhou ao serializar dataclass com `slots`.

Alteracoes:

- Criado `IsisAssistantCore`.
- Criados `EventBus`, `CommandRouter`, `ToolRegistry` e `HealthMonitor`.
- Adicionado comando `python -m aurora.cli core`.
- Criado `docs/CORE.md`.

Validacao:

- Testes focados: 12 passed.
- CLI `python -m aurora.cli core status`: retornou status `ok`.

Resultado:

- Fase 7 concluida.
- Nucleo inicia, processa comandos, audita eventos e executa shutdown seguro.

## 2026-07-28 - Fase 8 ISIS

Problemas identificados:

- Roteador selecionava modelo, mas nao havia camada de geracao.
- Ollama existe localmente, mas nao ha modelos instalados.

Alteracoes:

- Criado `aurora.core.model_provider`.
- Criados providers Mock, Ollama, llama.cpp e LM Studio.
- `IsisAssistantCore.generate_text()` conecta roteador a provider.
- Adicionado comando `python -m aurora.cli generate`.
- Criado `docs/LOCAL_MODELS.md`.

Validacao:

- Testes focados: 20 passed.
- `python -m aurora.cli generate "corrija este codigo"` retornou provider `mock`.
- `ollama list`: sem modelos.
- `nvidia-smi`: RTX 3060, 12288 MB total, 10490 MB livre.

Resultado:

- Fase 8 concluida.
- Geracao real aguarda instalacao/autorizacao de modelo local.

## 2026-07-28 - Fase 9 ISIS

Problemas identificados:

- Memoria permanente ainda nao tinha indice de projetos/notas do CEREBRO VIVO.
- Embeddings exigiriam modelo local ainda nao instalado.

Alteracoes:

- Criado `aurora.core.project_memory`.
- Criado banco SQLite de memoria de projetos.
- Adicionados comandos CLI `index-obsidian` e `project-search`.
- Criado `docs/PROJECT_MEMORY.md`.

Validacao:

- Testes focados: 10 passed.
- Indexacao amostral: 1000 notas em 10067 ms.
- Indexacao completa: 83194 Markdown em 650910 ms.
- Banco gerado: 52465664 bytes.

Resultado:

- Fase 9 concluida com busca textual local.
- Embeddings e projeto heuristico refinado ficam para fases seguintes.

## 2026-07-28 - Fase 10 ISIS

Problemas identificados:

- Faltava conector Obsidian formal separado da memoria de projetos.
- Parser YAML simples falhou em frontmatter com listas abaixo de chave vazia.

Correcoes:

- Criado `aurora.integrations.obsidian`.
- Criado `scripts/phase10_obsidian_readonly.py`.
- Parser YAML ajustado para listas.
- Criado banco `obsidian_readonly.sqlite`.

Validacao:

- Testes focados: 4 passed.
- Escaneadas 83194 notas.
- Criados 82194 registros e 1000 permaneceram inalterados da amostra.
- Checklists detectados: 48624; concluidos: 289.

Resultado:

- Fase 10 concluida.
- Cofre permaneceu somente leitura.

## 2026-07-28 - Fase 11 ISIS

Problemas identificados:

- Faltava busca unificada entre memoria de projetos e metadados Obsidian.
- Filtro por projeto nao deve usar fonte sem projeto consolidado.

Alteracoes:

- Criado `aurora.core.hybrid_search`.
- Adicionado comando CLI `search`.
- Criado `docs/HYBRID_SEARCH.md`.
- Criado `reports/phase11_hybrid_search.md`.

Validacao:

- Testes focados: 9 passed.
- `python -m aurora.cli search ISIS --limit 5` retornou resultados locais.

Resultado:

- Fase 11 concluida.
- Busca hibrida inicial operacional, sem embeddings.

## 2026-07-28 - Fase 12 ISIS

Problemas identificados:

- Inferencia anterior gerava muitos nomes de projeto.
- Algumas areas do cofre sao agregadores, nao projetos confirmados.

Alteracoes:

- Criado `aurora.core.project_catalog`.
- Criado banco `project_catalog.sqlite`.
- Adicionados comandos CLI `consolidate-projects` e `projects`.
- Criado `docs/PROJECT_CATALOG.md`.

Validacao:

- Testes focados: 8 passed.
- Consolidacao real: 29 candidatos.

Resultado:

- Fase 12 concluida como catalogo de candidatos.
- Confirmacao manual/refino fica para etapa posterior.

## 2026-07-28 - Fase 13 ISIS

Problemas identificados:

- Decisoes e bugs estavam apenas misturados no indice de notas.
- Classificacao e heuristica e pode conter ruido.

Alteracoes:

- Criado `aurora.core.knowledge_records`.
- Criado banco `knowledge_records.sqlite`.
- Adicionados comandos CLI para importar e consultar decisoes/bugs.
- Criado `docs/KNOWLEDGE_RECORDS.md`.

Validacao:

- Testes focados: 9 passed.
- Importadas 1080 decisoes e 10612 bugs.

Resultado:

- Fase 13 concluida como base inicial consultavel.

## 2026-07-28 - Fase 14 ISIS

Alteracoes:

- Criado `aurora.voice.factory`.
- Conectado `VoiceSessionManager` ao `IsisAssistantCore`.
- Adicionado comando `voice-core`.
- Criado `docs/VOICE_CORE.md`.

Validacao:

- Testes focados: 13 passed.
- CLI `voice-core` retornou transcricao, resposta mock e audio mock.

Resultado:

- Fase 14 concluida sem ativar microfone real nem baixar modelos.

## 2026-07-28 - Fase 15 ISIS

Alteracoes:

- Criado `SecurityGuard`.
- Adicionados estados de permissao.
- Conectada ferramenta `security_status`.
- Criado `docs/SECURITY_GUARD.md`.

Validacao:

- Testes focados: 8 passed.
- CLI `security-status` retornou pastas permitidas/protegidas e comandos bloqueados.

Resultado:

- Fase 15 concluida.

## 2026-07-28 - Fase 16 ISIS

Alteracoes:

- Criado pacote `aurora.perception`.
- Implementada visao de tela manual/mock.
- Adicionada politica de privacidade para tela.
- Adicionada redacao de dados sensiveis.
- Adicionados comandos `screen-status` e `screen-mock`.
- Criado `docs/SCREEN_VISION.md`.

Validacao:

- Testes focados da Fase 16: 4 passed.
- CLI `screen-status`: retornou captura real desativada.
- CLI `screen-mock`: mascarou senha e detectou campo/botao.
- Suite completa apos Fase 16: 80 passed.

Resultado:

- Captura real continua desativada.
- Fase 16 limitada a analise mock/manual segura.

## 2026-07-28 - Fase 17 ISIS

Alteracoes:

- Criado pacote `aurora.automation`.
- Implementado planejamento de acoes de UI.
- Implementada politica de aprovacao por acao.
- Adicionado executor mock sem acao real no Windows.
- Adicionados comandos `ui-plan` e `ui-mock-action`.
- Criado `docs/UI_AUTOMATION.md`.

Validacao:

- Testes focados da Fase 17: 4 passed.
- CLI `ui-plan`: gerou acao `CLICK` pendente de aprovacao.
- CLI `ui-mock-action --approve`: executou apenas em mock.
- CLI sensivel `banco confirmar pagamento`: bloqueado por politica.
- Suite completa apos Fase 17: 84 passed.

Resultado:

- Automacao real permanece desativada.
- Fase 17 limitada a planejamento e execucao mock aprovada.

## 2026-07-28 - Fase 18 ISIS

Alteracoes:

- Criada ponte entre visao de tela e automacao controlada.
- Adicionada sugestao de acao baseada em botoes/campos detectados.
- Adicionado bloqueio por baixa confianca.
- Adicionado comando `screen-ui-suggest`.
- Criado `docs/SCREEN_AUTOMATION_BRIDGE.md`.

Validacao:

- Testes focados da Fase 18: 4 passed.
- CLI `screen-ui-suggest "salvar"`: sugeriu `CLICK` em `Botao salvar`.
- CLI com baixa confianca: bloqueado por `low confidence`.
- Suite completa apos Fase 18: 88 passed.

Resultado:

- OCR real e execucao real continuam pendentes.
- Fluxo mock tela -> sugestao -> aprovacao -> execucao mock implementado.

## 2026-07-28 - Fase 19 ISIS

Alteracoes:

- Criado logger JSONL de acoes de UI.
- Integrada auditoria aos comandos `ui-mock-action` e `screen-ui-suggest`.
- Adicionado status local de permissoes.
- Adicionado comando para consultar ultimas acoes auditadas.
- Criado `docs/ACTION_AUDIT.md`.

Validacao:

- Testes focados da Fase 19: 4 passed.
- CLI `ui-permissions-status`: retornou execucao real desativada e aprovacao por acao ativa.
- CLI `ui-mock-action --approve`: executou mock e gravou auditoria.
- CLI `ui-action-audit --limit 3`: retornou registros JSONL.
- Corrigido custo do `coding-local-mock` para evitar fallback por VRAM real.
- Suite completa final: 92 passed.

Resultado:

- Auditoria local implementada.
- UI grafica de permissoes ainda pendente.

## 2026-07-28 - Fase 20 ISIS

Alteracoes:

- Criado pacote `aurora.ui`.
- Criado snapshot local de dashboard.
- Criada UI Tkinter com abas de status, permissoes e memoria.
- Adicionados comandos `ui-snapshot` e `ui-dashboard`.
- Criado `docs/LOCAL_DASHBOARD.md`.

Validacao:

- Testes focados da Fase 20: 2 passed.
- CLI `ui-snapshot`: retornou status/permissoes/memoria.
- Corrigido contador de notas para tabela real `indexed_notes`.
- Snapshot real exibiu 83194 notas indexadas.
- Suite completa apos Fase 20: 94 passed.

Resultado:

- UI local criada sem ativar recursos reais sensiveis.

## 2026-07-28 - Fase 21 ISIS

Alteracoes:

- Criado autenticador local PBKDF2-SHA256.
- Adicionado bootstrap por variavel de ambiente.
- Adicionada verificacao para troca de perfil.
- Adicionados comandos `auth-status`, `auth-bootstrap` e `profile-set`.
- Criado `docs/LOCAL_AUTH.md`.

Validacao:

- Testes focados da Fase 21: 3 passed.
- CLI `auth-status`: retornou `configured=false`.
- CLI `profile-set CONTROLLED` sem credencial: bloqueado por autenticacao.
- Suite completa apos Fase 21: 97 passed.

Resultado:

- Troca de perfil agora tem ponto de autenticacao local.
- Credencial real nao foi criada porque depende de senha definida pelo usuario.

## 2026-07-28 - Fase 22 ISIS

Alteracoes:

- Criado servico de controles de privilegio para UI.
- Adicionado controle de perfil na aba `Permissions`.
- Adicionado prompt de senha em memoria para mudanca de perfil.
- Adicionado comando `ui-privileges-status`.
- Criado `docs/PRIVILEGE_UI.md`.

Validacao:

- Testes focados da Fase 22: 3 passed.
- CLI `ui-privileges-status`: retornou controles bloqueados sem autenticacao configurada.
- Suite completa apos Fase 22: 100 passed.

Resultado:

- Controles editaveis existem, mas permanecem bloqueados sem autenticacao local configurada.

## 2026-07-28 - Fase 23 ISIS

Alteracoes:

- Criado logger de auditoria de privilegios.
- Auditadas mudancas e tentativas bloqueadas de perfil.
- Adicionado botao de emergencia na UI local.
- Adicionados comandos `emergency-stop` e `privilege-audit`.
- Criado `docs/PRIVILEGE_AUDIT.md`.

Validacao:

- Testes focados da Fase 23: 4 passed.
- CLI `emergency-stop`: alterou perfil real para `MEDIUM`.
- CLI `privilege-audit --limit 3`: retornou registros JSONL.
- Suite completa apos Fase 23: 104 passed.

Resultado:

- Parada de emergencia implementada e auditavel.

## 2026-07-28 - Fase 24 ISIS

Alteracoes:

- Criado servico de painel de habilidades.
- Adicionada aba `Skills` ao dashboard local.
- Adicionados comandos `ui-skills-snapshot` e `ui-skill-run`.
- Execucao de habilidades usa autorizacao e sandbox.
- Criado `docs/SKILLS_PANEL.md`.

Validacao:

- Testes focados da Fase 24: 5 passed.
- CLI `ui-skills-snapshot`: listou habilidades instaladas.
- CLI `ui-skill-run project_list --arg root=D:/ISIS_IA --approve`: executou em sandbox.
- Suite completa apos Fase 24: 109 passed.

Resultado:

- Painel inicial de habilidades implementado.

## 2026-07-28 - Fase 25 ISIS

Alteracoes:

- Criado servico de painel de memoria.
- Adicionada listagem de registros locais na aba `Memory`.
- Adicionados comandos `ui-memory-propose`, `ui-memory-list` e `ui-memory-status`.
- Registros novos entram como `PROPOSED`.
- Criado `docs/MEMORY_PANEL.md`.

Validacao:

- Testes focados da Fase 25: 4 passed.
- CLI `ui-memory-propose`: criou registro `a80ef97b-1100-4f33-b41c-59bfab7de764`.
- CLI `ui-memory-list --status PROPOSED`: listou registro proposto.
- CLI `ui-memory-status ... CONFIRMED`: confirmou registro.
- Suite completa apos Fase 25: 113 passed.

Resultado:

- Memoria editavel local implementada sem escrita no Obsidian.

## 2026-07-28 - Fase 26 ISIS

Alteracoes:

- Criado logger de auditoria de memoria.
- Auditadas propostas, confirmacoes e rejeicoes.
- Adicionados botoes `Confirm` e `Reject` na UI.
- Adicionado comando `memory-approval-audit`.
- Criado `docs/MEMORY_APPROVAL_AUDIT.md`.

Validacao:

- Testes focados da Fase 26: 3 passed.
- CLI `ui-memory-propose`: gravou auditoria em `memory_approvals.jsonl`.
- CLI `memory-approval-audit --limit 3`: retornou registros JSONL.
- Corrigido custo de modelos mock para nao depender de VRAM real disponivel.
- Suite completa apos Fase 26: 116 passed.

Resultado:

- Auditoria de aprovacao de memoria implementada.

## 2026-07-28 - Fase 27 ISIS

Alteracoes:

- Adicionado filtro de status na aba `Memory`.
- Adicionada exportacao local de memoria.
- Adicionado comando `ui-memory-export`.
- Criado `docs/MEMORY_EXPORT.md`.

Validacao:

- Testes focados da Fase 27: 3 passed.
- CLI `ui-memory-export`: gerou `D:\ISIS_IA\ISIS\reports\memory_report.json`.
- Suite completa apos Fase 27: 119 passed.

Resultado:

- Filtros e exportacao de memoria implementados.

## 2026-07-28 - Fase 28 ISIS

Alteracoes:

- Criado relatorio consolidado de auditoria local.
- Adicionado comando `audit-report`.
- Criado `docs/AUDIT_REPORT.md`.

Validacao:

- Testes focados da Fase 28: 3 passed.
- CLI `audit-report`: gerou `D:\ISIS_IA\ISIS\reports\audit_report.json`.
- Suite completa apos Fase 28: 122 passed.

Resultado:

- Consolidacao de auditoria implementada.

## 2026-07-28 - Fase 29 ISIS

Alteracoes:

- Criado servico de integridade de relatorios.
- Adicionado manifesto SHA-256.
- Adicionados comandos `report-integrity` e `report-integrity-verify`.
- Criado `docs/REPORT_INTEGRITY.md`.

Validacao:

- Testes focados da Fase 29: 3 passed.
- CLI `report-integrity`: gerou `D:\ISIS_IA\ISIS\reports\report_integrity.json`.
- CLI `report-integrity-verify`: retornou `ok=true`.
- Suite completa apos Fase 29: 125 passed.

Resultado:

- Integridade basica de relatorios implementada.

## 2026-07-28 - Fase 30 ISIS

Alteracoes:

- Criado servico de assinatura local.
- Adicionada chave local HMAC-SHA256.
- Adicionados comandos `signature-key-status`, `sign-report` e `verify-signature`.
- Criado `docs/LOCAL_SIGNATURE.md`.

Validacao:

- Testes focados da Fase 30: 3 passed.
- CLI `sign-report`: gerou `D:\ISIS_IA\ISIS\reports\report_integrity.sig.json`.
- CLI `verify-signature`: retornou `ok=true`.
- Suite completa apos Fase 30: 128 passed.

Resultado:

- Assinatura local de relatorios implementada.

## 2026-07-28 - Fase 31 ISIS

Alteracoes:

- Adicionado status detalhado da chave local.
- Adicionada rotacao com backup previo.
- Adicionado comando `signature-key-rotate`.
- Criado `docs/SIGNATURE_KEY_ROTATION.md`.

Validacao:

- Testes focados Fases 30/31: 7 passed.
- CLI `signature-key-status`: chave configurada, backups: 3.
- CLI `signature-key-rotate`: executado com backup previo.
- CLI `sign-report` e `verify-signature`: assinatura operacional refeita e validada.
- Suite completa apos Fase 31: 132 passed.

Resultado:

- Rotacao local de chave implementada sem apagar chave antiga.

## 2026-07-28 - Fase 32 ISIS

Alteracoes:

- Criado inspetor nao destrutivo de ACL.
- Adicionado comando `signature-key-acl-status`.
- Criado `docs/KEY_ACL.md`.

Validacao:

- Testes focados da Fase 32: 3 passed.
- CLI `signature-key-acl-status`: confirmou chave existente e ACL nao restrita.
- Suite completa apos Fase 32: 135 passed.

Resultado:

- Risco identificado: chave herda permissao de modificacao para usuarios autenticados.

## 2026-07-28 - Fase 33 ISIS

Alteracoes:

- Criado fluxo de aplicacao controlada de ACL.
- Adicionado dry-run por padrao.
- Adicionado rollback via backup de ACL.
- Criado `docs/KEY_ACL_APPLY.md`.

Validacao:

- Testes focados da Fase 33: 3 passed.
- CLI `signature-key-acl-apply`: dry-run gerou plano e caminho de backup.
- Suite completa apos Fase 33: 138 passed.

Resultado:

- Aplicacao de ACL implementada; aplicacao operacional depende de `--apply`.

## 2026-07-28 - Fase 34 ISIS

Alteracoes:

- Executada aplicacao operacional de ACL na chave local.
- Backup ACL criado antes da alteracao.
- Heranca removida do arquivo.
- Permissao final restrita a Administradores, SISTEMA e usuario atual.
- Criado `docs/KEY_ACL_OPERATIONAL.md`.

Validacao:

- CLI `signature-key-acl-status`: `restricted=true`.
- CLI `verify-signature`: `ok=true`.
- Suite completa apos Fase 34: 138 passed.

Resultado:

- Chave de assinatura agora esta com ACL restrita.

## 2026-07-28 - Fase 35 ISIS

Alteracoes:

- Criado painel de auditoria.
- Adicionada aba `Audit` ao dashboard.
- Adicionado comando `ui-audit-snapshot`.
- Criado `docs/AUDIT_PANEL.md`.

Validacao:

- Testes focados da Fase 35: 2 passed.
- CLI `ui-audit-snapshot`: integridade `true`, chave restrita `true`.
- Suite completa apos Fase 35: 140 passed.

Resultado:

- Auditoria e integridade agora aparecem no dashboard.

## 2026-07-28 - Fase 36 ISIS

Alteracoes:

- Criado fluxo de manutencao de relatorios.
- Adicionado comando `reports-regenerate`.
- Adicionado botao `Regenerate reports`.
- Criado `docs/REPORT_MAINTENANCE.md`.

Validacao:

- Testes focados da Fase 36: 2 passed.
- CLI `reports-regenerate`: regenerou auditoria, integridade e assinatura.
- Suite completa apos Fase 36: 142 passed.

Resultado:

- Regeneracao serial de relatorios implementada.

## 2026-07-28 - Fase 37 ISIS

Alteracoes:

- Adicionado historico local de regeneracao.
- Adicionado comando `reports-history`.
- Criado `docs/REPORT_HISTORY.md`.

Validacao:

- Testes focados da Fase 37: 2 passed.
- CLI `reports-regenerate` + `reports-history`: historico gravado e consultado.
- Suite completa apos Fase 37: 144 passed.

Resultado:

- Historico local de manutencao de relatorios implementado.

## 2026-07-28 - Fase 38 ISIS

Alteracoes:

- Adicionados campos de historico ao painel de auditoria.
- Criado `docs/AUDIT_HISTORY_PANEL.md`.

Validacao:

- Testes focados da Fase 38: 6 passed.
- CLI `reports-regenerate`: regenerou relatorios e assinatura.
- CLI `ui-audit-snapshot`: integridade `true`, chave restrita `true`.
- Corrigido manifesto para ignorar `*.sig.json`.
- Suite completa apos Fase 38: 145 passed.

Resultado:

- Historico de relatorios visivel no snapshot/painel de auditoria.

## 2026-07-28 - Fase 39 ISIS

Alteracoes:

- Baixados modelos locais via Ollama.
- Migrado runtime Ollama para `D:\ISIS_IA\ISIS\runtime\ollama`.
- Configurado `OLLAMA_MODELS` do usuario para `D:\ISIS_IA\ISIS\models\ollama`.
- Conectado `OllamaModelProvider` ao nucleo antes do mock.
- Atualizadas rotas reais em `data/config.json`.
- Atualizada documentacao `docs/LOCAL_MODELS.md`.
- Baixado `Ternary-Bonsai-27B-Q2_0.gguf` do Hugging Face.
- Criada documentacao `docs/TERNARY_BONSAI_27B.md`.

Modelos instalados:

- `qwen2.5-coder:14b`.
- `llama3.1:8b`.
- `nomic-embed-text:latest`.
- `deepseek-r1:8b`.
- `Ternary-Bonsai-27B-Q2_0.gguf`.

Validacao:

- `ollama.exe` em `D:\ISIS_IA\ISIS\runtime\ollama`.
- `ollama list` usando `D:\ISIS_IA\ISIS\models\ollama` lista os modelos principais.
- Rota de codigo seleciona `qwen2.5-coder:14b`.
- Rota de memoria seleciona `nomic-embed-text:latest`.
- Geracao com `qwen2.5-coder:14b` retornou via provider `ollama`.
- Suite completa: 145 passed.
- Exclusao de pastas antigas em `C:\Users\Rodrigo Tejada` bloqueada pela politica da sessao.

Resultado:

- AURORA preparado para geracao local real com fallback mock.

## 2026-07-28 - Fase 40 ISIS

Alteracoes:

- Criado `aurora.core.embeddings`.
- Adicionado provider de embeddings via Ollama.
- Adicionado indice SQLite `memory_embeddings.sqlite`.
- Adicionados comandos `memory-embed` e `memory-semantic-search`.
- Criada documentacao `docs/MEMORY_EMBEDDINGS.md`.

Validacao:

- Testes focados da Fase 40: 2 passed.
- `memory-embed --limit 10`: indexacao real com `nomic-embed-text:latest`.
- Segunda execucao de `memory-embed`: `skipped=2`.
- `memory-semantic-search "embeddings locais no ssd"` retornou a memoria correta em primeiro lugar.
- Suite completa apos Fase 40: 147 passed.

Resultado:

- Memoria confirmada agora tem busca semantica local real.

## 2026-07-28 - Fase 41 ISIS

Alteracoes:

- Baixado e instalado runtime `llama.cpp` b10173 CUDA 12.4.
- Tentada integracao do `Ternary-Bonsai-27B-Q2_0.gguf` via Ollama.
- Tentada execucao do `Ternary-Bonsai-27B-Q2_0.gguf` via `llama.cpp`.
- Baixado `KAT-Coder-V2.5-Dev` completo do Hugging Face.
- Criado registro `data/external_models.json`.
- Criado script `scripts/hf_models_status.ps1`.
- Criada documentacao `docs/KAT_CODER_V2_5_DEV.md`.

Validacao:

- Bonsai SHA-256 local confere com Hugging Face.
- Ollama recusou Bonsai: `tensor "output.weight" size overflow`.
- `llama.cpp` recusou Bonsai: offset inconsistente em `output_norm.weight`.
- KAT-Coder contem 13 shards safetensors e metadados completos.

Resultado:

- Modelos HF estao baixados e registrados.
- Bonsai e KAT nao foram colocados como rota ativa local por bloqueios tecnicos reais.

## 2026-07-28 - Fase 42 ISIS

Alteracoes:

- Baixado `qwen3-coder:30b` via Ollama.
- Adicionado `qwen3-coder:30b` como prioridade 1 para `CODING`.
- Mantido `qwen2.5-coder:14b` como fallback de codigo.
- Excluido KAT-Coder local por solicitacao do usuario.
- Atualizado `data/external_models.json`.

Validacao:

- `ollama list` mostra `qwen3-coder:30b`.
- `route "corrija este codigo..."` seleciona `qwen3-coder:30b`.
- `generate "corrija este codigo Python..."` retornou via provider `ollama`, modelo `qwen3-coder:30b`.
- Suite completa apos Fase 42: 147 passed.

Resultado:

- AURORA usa agora um modelo de codigo MoE compatível via Ollama, no lugar do KAT safetensors.

## 2026-07-28 - Fase 43 ISIS

Alteracoes:

- Adicionado `ProjectEmbeddingIndex`.
- Adicionados comandos `project-embed` e `project-semantic-search`.
- Criado banco `project_note_embeddings.sqlite`.
- Criada documentacao `docs/PROJECT_EMBEDDINGS.md`.

Validacao:

- Testes focados da Fase 43: 2 passed.
- `project-embed --limit 5`: `indexed=5`.
- Reexecucao de `project-embed --limit 5`: `skipped=5`.
- `project-semantic-search "ISIS memoria local"` retornou resultados reais.
- Suite completa apos Fase 43: 149 passed.

Resultado:

- Indice grande de projetos agora tem busca semantica local em lotes.

## 2026-07-28 - Fase 44 ISIS

Alteracoes:

- Corrigida fila de pendentes do `ProjectEmbeddingIndex`.
- Adicionado progresso de embeddings de projetos.
- Adicionado processamento multi-lote.
- Criados comandos `project-embed-progress` e `project-embed-batch`.
- Criada documentacao `docs/PROJECT_EMBEDDING_BATCH.md`.

Validacao:

- Testes focados da Fase 44: 3 passed.
- `project-embed-progress`: total 83194, indexed 5, pending 83189.
- `project-embed-batch --batch-size 5 --max-batches 2`: indexou mais 10 notas.
- Progresso apos lote: indexed 15, pending 83179.
- Suite completa apos Fase 44: 150 passed.

Resultado:

- Indexacao semantica de projetos agora progride corretamente em lotes.

## 2026-07-28 - Fase 45 ISIS

Alteracoes:

- Adicionado worker controlado de embeddings de projetos.
- Adicionado historico JSONL do worker.
- Criados comandos `project-embed-worker` e `project-embed-history`.
- Criada documentacao `docs/PROJECT_EMBEDDING_WORKER.md`.

Validacao:

- Testes focados da Fase 45: 4 passed.
- `project-embed-worker --batch-size 5 --max-batches 2 --max-seconds 60`: indexou 10 notas.
- `project-embed-history --limit 3`: retornou execucao do worker.
- `project-embed-progress`: indexed 25, pending 83169.
- Suite completa apos Fase 45: 151 passed.

Resultado:

- Indexacao semantica pode continuar em execucoes curtas e auditaveis.

## 2026-07-28 - Fase 46 ISIS

Alteracoes:

- Criado `aurora.ui.hud_dashboard`.
- Adicionado comando `ui-hud`.
- Adicionado comando `ui-hud-snapshot`.
- Criada interface Tkinter escura estilo central de comando IA.
- Criado avatar animado em Canvas.
- Criada documentacao `docs/HUD_INTERFACE.md`.

Validacao:

- Testes focados da Fase 46: 2 passed.
- `ui-hud-snapshot`: retornou status real com `qwen3-coder:30b`, `nomic-embed-text:latest`, 83194 notas e 25 embeddings de projetos.

Resultado:

- Projeto agora possui uma interface visual moderna para teste local.

## 2026-07-28 - Fase 47 ISIS

Alteracoes:

- Baixado Piper Windows para `D:\ISIS_IA\ISIS\runtime\piper`.
- Baixada voz `pt_BR-faber-medium`.
- Configurado `tts_engine=piper`.
- Adicionados comandos `voice-status` e `voice-speak`.
- HUD agora mostra status de voz e botao `VOZ TESTE`.
- Corrigido fallback seguro do `voice-core` para comandos bloqueados.
- Criada documentacao `docs/VOICE_PIPER_REAL.md`.

Validacao:

- `voice-status`: Piper e voz existem.
- `voice-speak "ISIS voz real local com Piper ativa."`: gerou WAV real.
- `voice-core --transcript "status"`: gerou WAV com engine `piper`.
- Testes focados da Fase 47: 4 passed.
- Suite completa apos Fase 47: 155 passed.

Resultado:

- ISIS ja responde em audio gerado localmente por Piper.
- Microfone/STT real ainda nao foram ativados.

## 2026-07-28 - Fase 48 ISIS

Alteracoes:

- HUD Tkinter conectada ao `IsisAssistantCore`.
- Campo de comando envia prompt real.
- Historico de conversa renderiza mensagens do usuario e da ISIS.
- Respostas geram audio Piper automaticamente quando TTS esta pronto.
- Botoes `MIC`, `ANEXO`, `ENVIAR` e `PARAR` ligados a estados/acoes reais.
- Criado servidor HUD web local em `aurora.ui.hud_web`.
- Adicionado comando `ui-hud-web`.
- Atualizada documentacao `docs/HUD_INTERFACE.md`.

Validacao:

- Testes focados da Fase 48: 7 passed.
- `ui-hud-snapshot`: retornou `qwen3-coder:30b`, Piper pronto e `stt_engine=mock`.
- Servidor escutando em `127.0.0.1:8765`.
- `/api/snapshot`: retornou JSON real.
- `/api/voice-test`: gerou WAV Piper.
- `/api/chat` com `status`: retornou bloqueio seguro por politica e WAV Piper.

Resultado:

- Link local de teste ativo: `http://127.0.0.1:8765/`.
- Microfone real e anexos continuam pendentes por projeto/politica.

## 2026-07-28 - Framework Development_Framework

Problemas identificados:

- Havia risco real de continuar alterando a interface no projeto errado.
- Faltava documento mestre local para fixar escopo, portas, voz e arquivos ativos.

Alteracoes:

- Criado `00_MASTER.md`.
- Criado `AGENTS.md`.
- Criada pasta `docs/framework`.
- Criados registros de tarefas, decisoes, bugs, retomada rapida e criterio de pronto.
- Criado `.gitignore` basico para caches e artefatos locais.

Resultado:

- `Development_Framework` aplicado sobre `D:\ISIS_IA\AURORA`.
- HUD web correto fixado como `aurora/ui/hud_web.py`.
- Link oficial da IA fixado como `http://127.0.0.1:8765/`.

## 2026-07-28 - Correcao HUD web mic/voz/navegacao

Problemas identificados:

- Botao `MIC` nao capturava audio.
- Voz Piper local soava robotica.
- Menu lateral nao trocava paineis.
- HUD web estava visualmente pobre e com area central vazia.

Alteracoes:

- `MIC` conectado a Web Speech Recognition em `pt-BR`.
- `VOZ NATURAL` conectado a `speechSynthesis` com selecao de voz `pt-BR`.
- Piper mantido como fallback de audio local.
- Menu lateral agora alterna paineis funcionais.
- `ANEXO` abre seletor local de arquivos.
- `PARAR` cancela voz, ditado e resposta pendente no cliente.
- Interface web recebeu paineis operacionais de memoria, projetos, documentos, automacoes, agenda e configuracoes.

Validacao:

- `python -m py_compile aurora\ui\hud_web.py`.
- `python -m pytest tests\test_phase48_operational_hud.py -q`: 3 passed.

## 2026-07-28 - Correcao TTS Markdown

Problema:

- A fala recebia a resposta bruta com Markdown, listas, links e blocos de codigo.

Alteracoes:

- Criado `aurora.voice.text.prepare_text_for_speech`.
- `speech_excerpt` agora usa a limpeza de fala.
- Providers Piper e mock sanitizam o texto imediatamente antes da sintese.
- HUD web retorna `speech_text` separado de `response` e usa `speech_text` no `speechSynthesis`.
- Ajustado `aurora.voice.__init__` para evitar ciclo de import ao importar o sanitizador isoladamente.

Validacao:

- `python -m py_compile aurora\voice\__init__.py aurora\voice\text.py aurora\voice\providers.py aurora\voice\local_providers.py aurora\ui\hud_dashboard.py aurora\ui\hud_web.py`.
- `python -m pytest tests\test_phase48_operational_hud.py tests\test_phase14_voice_core.py tests\test_voice.py tests\test_local_voice_providers.py -q --basetemp .tmp\pytest-tts-clean`: 13 passed.

## 2026-07-28 - Correcao mic auto envio e rota de codigo

Problemas:

- O microfone transcrevia, mas nao enviava a pergunta automaticamente.
- Pergunta de codigo podia retornar `[mock:coding-local-mock]`.

Alteracoes:

- `recognition.onresult` agora chama `sendPrompt()` apos transcricao final.
- Adicionada trava `sending` no HUD web para evitar envio duplicado.
- Roteamento detecta plural/acento de `codigo/códigos`.
- `ResourceMonitor.can_load` permite modelo real via RAM quando VRAM esta baixa.

Validacao:

- `python -m py_compile aurora\core\resources.py aurora\core\routing.py aurora\ui\hud_web.py`.
- `python -m pytest tests\test_phase48_operational_hud.py tests\test_config_runtime_cli.py tests\test_audit_resources.py tests\test_routing.py -q --basetemp .tmp\pytest-voice-code`: 19 passed.
- Rota real para `você consegue criar códigos`: `CODING qwen3-coder:30b VRAM insufficient; using RAM`.

## 2026-07-28 - Correcao exibicao de embeddings no chat

Problema:

- A conversa inicial mostrava backlog tecnico de embeddings pendentes.

Alteracoes:

- HUD web e Tkinter trocaram a bolha por mensagem curta de memoria pronta.
- Numeros de embeddings permanecem nos paineis operacionais.

Validacao:

- `python -m py_compile aurora\ui\hud_web.py aurora\ui\hud_dashboard.py`.
- `python -m pytest tests\test_phase48_operational_hud.py tests\test_phase46_hud_dashboard.py -q --basetemp .tmp\pytest-embed-hud`: 6 passed.
- `project-embed-worker --batch-size 10 --max-batches 1 --max-seconds 120`: indexou 10 notas; progresso `35/83194`, pendentes `83159`.

## 2026-07-28 - HUD assincrono com historico e projetos

Diagnostico:

- O request `/api/chat` executava modelo e TTS de forma sincrona no handler.
- A interface ficava aguardando sem estados intermediarios confiaveis.

Alteracoes:

- Criado `aurora.core.conversations.ConversationStore`.
- Criado banco local `D:\ISIS_IA\ISIS\data\databases\hud_conversations.sqlite`.
- HUD web passou a iniciar jobs por `/api/chat` e consultar `/api/chat-status`.
- Adicionado cancelamento por `/api/chat-cancel`.
- Conversas salvam mensagens do usuario e da IA, modelo, metadata e resumo simples.
- Projetos sao persistidos com status, objetivo, diretorio, tecnologias, regras, decisoes e permissao.
- Sidebar recebeu novo projeto, busca, projetos recentes, conversas recentes, favoritos, arquivados e lixeira.
- Respostas ganharam copiar, tentar novamente e editar pergunta.

Validacao:

- `python -m py_compile aurora\core\conversations.py aurora\ui\hud_web.py`.
- `python -m pytest tests\test_hud_conversations.py tests\test_phase48_operational_hud.py tests\test_phase46_hud_dashboard.py -q --basetemp .tmp\pytest-hud-history`: 8 passed.
- HTTP real em `http://127.0.0.1:8765`: HTML assincrono ok, job iniciado, status `concluido`, conversa com 2 mensagens salva.

Rollback:

- Restaurar `aurora\ui\hud_web.py` para o handler sincrono anterior.
- Remover chamadas a `ConversationStore`.
- Manter ou apagar manualmente `D:\ISIS_IA\ISIS\data\databases\hud_conversations.sqlite` conforme necessidade.

## 2026-07-28 - Correcao footer/input oculto apos resposta longa

Diagnostico:

- Apos resposta longa sobre codigo, o status ficava em `Resposta concluida`, mas o usuario nao via campo de texto nem botoes de voz.
- A causa era layout: `.app` com `min-height:100vh` e `overflow:hidden` permitia que o footer fosse empurrado para fora da area visivel.

Alteracoes:

- HUD desktop fixado em `height:100vh`.
- Linha central do grid alterada para `minmax(0,1fr)`.
- `.workspace` recebeu `min-height:0` para rolagem interna correta.
- Criado `unlockInput()` para liberar envio e focar o input apos conclusao, cancelamento ou erro.

Validacao:

- `python -m py_compile aurora\ui\hud_web.py`.
- `python -m pytest tests\test_phase48_operational_hud.py -q --basetemp .tmp\pytest-hud-footer`: 4 passed.

## 2026-07-28 - Voz local modular

Pedido:

- Implementar base de voz feminina natural, gratuita, offline, com fallback, cache, STT local preparado, interrupcao e configuracao.

Backup:

- Criado backup previo em `backups\manual\voice_architecture_20260728_224115`.

Alteracoes:

- Criado `VoiceManager` e `VoiceRouter`.
- Criados subpacotes `aurora.voice.tts` e `aurora.voice.stt`.
- Piper foi adaptado como engine modular e fallback local.
- Kokoro e Chatterbox foram registrados como engines opcionais indisponiveis ate validacao local real de modelo pt-BR.
- Criado `AudioCache` por hash de texto normalizado, motor, voz, velocidade e emocao.
- Criado `PortugueseSpeechNormalizer`.
- Criado `SpeechQueue`, `VoiceActivityDetector` e `InterruptionManager`.
- HUD web recebeu diagnostico de voz e limpeza de cache.
- CLI recebeu `voice-test`, `voice-cache-clear` e `voice-benchmark`.
- Criadas docs `VOICE_ARCHITECTURE`, `VOICE_INSTALLATION`, `VOICE_CONFIGURATION`, `VOICE_TROUBLESHOOTING`, `VOICE_BENCHMARK` e `VOICE_CHANGELOG`.

Limitacoes:

- Nao foi definido Kokoro/Chatterbox como padrao porque nao ha pacote/modelo pt-BR validado localmente nesta sessao.
- STT server-side real continua dependendo de binario/modelo `whisper.cpp` configurado.
- Medicao RAM/VRAM do benchmark fica pendente ate motor neural local estar instalado.

Validacao:

- `python -m py_compile` nos modulos de voz, HUD, CLI e config.
- `python -m pytest tests\test_voice_architecture.py tests\test_voice.py tests\test_local_voice_providers.py tests\test_phase47_voice_hud.py tests\test_phase48_operational_hud.py -q --basetemp .tmp\pytest-voice-architecture`: 16 passed.
- `python -m aurora.cli voice-status`: Piper disponivel, Kokoro/Chatterbox indisponiveis sem modelo local.
- `python -m aurora.cli voice-test "Bom dia, Rodrigo. Estou pronta para ajudar."`: WAV gerado via Piper em 2027 ms.
- Segunda execucao de `voice-test`: cache hit em 1 ms.
- `python -m aurora.cli voice-benchmark`: gerou `D:\ISIS_IA\ISIS\logs\voice_benchmark.json` e `.md`.
- HUD reiniciado em `http://127.0.0.1:8765/`; `/api/voice-status` retornou status dos motores.

## 2026-07-28 - Rolagem da conversa HUD web

Diagnostico:

- Usuario relatou que a tela de mensagens nao tinha barra de rolagem e nao se comportava como chat.
- O container rolavel era `workspace`, mas a lista `#messages` nao tinha `overflow-y:auto` nem altura flex.

Alteracoes:

- `workspace` passa a conter paineis sem rolar diretamente.
- `#conversa.panel.active` passa a ser flex column.
- `#messages` recebe `overflow-y:auto`, `min-height:0` e scroll proprio.
- Adicionado `scrollMessagesToBottom()` para novas mensagens e carregamento de historico.

Validacao:

- `python -m py_compile aurora\ui\hud_web.py`.
- `python -m pytest tests\test_phase48_operational_hud.py -q --basetemp .tmp\pytest-hud-scroll`: 4 passed.
- HUD web reiniciado em `http://127.0.0.1:8765/`.
- Playwright com 80 mensagens artificiais: `overflowY=auto`, `clientHeight=433`, `scrollHeight=13071`, `hasScrollbar=true`, `atBottom=true`.

## 2026-07-28 - Compatibilidade Kokoro/Chatterbox

Diagnostico:

- Usuario corrigiu a interpretacao: Kokoro e Chatterbox nao devem ser tratados como rejeitados.
- O codigo anterior registrava esses motores como stubs sempre indisponiveis.

Alteracoes:

- Criado `ExternalCliTTSEngine`.
- Kokoro e Chatterbox agora herdam do adaptador CLI local.
- Configuracao aceita `kokoro_command`, `kokoro_model_dir`, `kokoro_voice`, `chatterbox_command`, `chatterbox_model_dir` e `chatterbox_voice`.
- Tambem e aceito `tts_manifest.json` no diretorio do motor.

Validacao:

- `python -m py_compile aurora\voice\tts\external_cli_engine.py aurora\voice\tts\kokoro_engine.py aurora\voice\tts\chatterbox_engine.py aurora\voice\tts\tts_factory.py aurora\core\config.py`.
- `python -m pytest tests\test_voice_architecture.py -q --basetemp .tmp\pytest-voice-compat`: 5 passed.
- `python -m pytest tests\test_voice_architecture.py tests\test_voice.py tests\test_local_voice_providers.py tests\test_phase47_voice_hud.py -q --basetemp .tmp\pytest-voice-compat-full`: 13 passed.
- `python -m pytest -q --basetemp .tmp\pytest-full-after-voice-compat`: 168 passed.
- `python -m aurora.cli voice-status`: Kokoro/Chatterbox aparecem como compativeis, aguardando comando local configurado; Piper segue disponivel.

## 2026-07-28 - Internet controlada, pesquisa e Central de Regras

Backup:

- `AURORA\backups\manual\internet_permissions_20260728_231848`.

Alteracoes:

- Criado pacote `aurora.internet`.
- Criado pacote `aurora.permissions`.
- Integrado `ResearchAgent` ao `IsisAssistantCore`.
- Criado `DownloadManager` seguro.
- Criados comandos CLI `internet-status`, `internet-test`, `internet-search`, `internet-download`, `internet-cache-clear`, `research-history`, `rules-parse`, `rules-apply`, `rules-history`, `permission-summary`, `permission-simulate`, `permission-temp-add`, `permission-profiles` e `permission-emergency-block`.
- HUD web recebeu aba `Internet` com status, teste, pesquisa, parser/aplicacao de regras, cache e bloqueio emergencial.
- Criada documentacao de Internet, seguranca web, pesquisa, memoria e permissoes.

Validacao:

- `python -m pytest tests\test_internet_permissions.py tests\test_config_runtime_cli.py tests\test_phase48_operational_hud.py tests\test_phase7_core.py -q --basetemp .tmp\pytest-internet-focused`: 23 passed.
- `python -m aurora.cli internet-status`: Internet `controlled`, provedor `duckduckgo_html+bing_html`.
- `python -m aurora.cli internet-test`: `ok=true`, HTTP 200.
- `python -m aurora.cli internet-search "Python pathlib official documentation" --approve`: 5 fontes, primeira `https://www.python.org/`.
- `python -m aurora.cli internet-download https://example.com/tool.exe --approve`: bloqueado por tipo `.exe`.
- `python -m pytest -q --basetemp .tmp\pytest-full-internet-permissions`: 175 passed.
- `python -m pytest -q --basetemp .tmp\pytest-full-internet-final`: 175 passed.
- `python -m pytest -q --basetemp .tmp\pytest-full-internet-final2`: 175 passed.
- HUD web reiniciado em `http://127.0.0.1:8765/`.
- `/api/internet-status`: `enabled=true`, `mode=controlled`.
- `/api/internet-search`: 5 fontes, primeira `https://www.python.org/`.

Limitacoes:

- Escrita em CEREBRO_VIVO permanece desativada por padrao.
- Navegador Playwright para paginas JavaScript ainda nao foi ativado.
- Comandos criticos por voz ainda precisam de autenticacao/PIN local.

## 2026-07-29 - Correcao voz local no HUD web

Diagnostico:

- Usuario informou que a HUD ainda puxava `Microsoft Maria - Portuguese (Brazil)`.
- Causa confirmada: JavaScript priorizava `speechSynthesis` do Windows/Chrome.

Alteracoes:

- Removido uso de `speechSynthesis` e `SpeechSynthesisUtterance` da HUD.
- Botao alterado para `VOZ LOCAL`.
- Respostas e teste de voz passam a tocar somente `audio_url` gerado pelo Piper.
- `MIC` permanece usando `SpeechRecognition` apenas para entrada por ditado.

Validacao:

- `python -m py_compile aurora\ui\hud_web.py`.
- `python -m pytest tests\test_phase48_operational_hud.py tests\test_phase47_voice_hud.py tests\test_voice_architecture.py -q --basetemp .tmp\pytest-hud-local-voice`: 11 passed.
- `python -m aurora.cli voice-test "ISIS usando voz local Piper."`: `engine=piper`, `voice=dii_pt-BR`.
- HUD web reiniciado em `http://127.0.0.1:8765/`.
- HTML servido: `speechSynthesis=false`, `SpeechSynthesisUtterance=false`, `Microsoft Maria=false`, `VOZ LOCAL=true`.
- `/api/voice-test`: WAV local gerado.
- `python -m pytest -q --basetemp .tmp\pytest-full-local-voice`: 175 passed.
