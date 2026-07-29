# Changelog

## 0.1.0 - 2026-07-28

- Criado projeto AURORA em `D:\ISIS_IA\AURORA`.
- Implementado nucleo de permissoes e perfis.
- Implementada auditoria JSONL com sanitizacao.
- Implementado monitor de recursos com fallback para RTX 3060 12 GB.
- Implementado roteador deterministico de modelos.
- Implementado fluxo de voz com providers mock.
- Implementada memoria SQLite e RAG textual.
- Implementado gerenciador de habilidades com Pydantic, sandbox, instalacao aprovada e rollback.
- Adicionadas 10 habilidades iniciais seguras.
- Adicionados 19 testes automatizados.

## 0.1.1 - 2026-07-28

- Adicionada configuracao persistente em `data/config.json`.
- Adicionado runtime central `AuroraRuntime`.
- Adicionados adaptadores locais seguros para `whisper.cpp`, Piper e wake word configuravel.
- Adicionada CLI `python -m aurora.cli`.
- Adicionados testes de configuracao, runtime, CLI e adaptadores locais.

## 0.1.2 - 2026-07-28

- Executada Fase 1 do prompt ISIS em modo somente leitura.
- Criado auditor `scripts/phase1_audit.py`.
- Gerados relatorios em `reports/`.
- Identificado cofre `E:\Projetos\CEREBRO_VIVO`.
- Adicionada documentacao `docs/CEREBRO_VIVO_MIGRATION.md`.
- Adicionados testes do auditor de Fase 1.

## 0.1.3 - 2026-07-28

- Executada Fase 2 do prompt ISIS.
- Criada estrutura `D:\ISIS_IA\ISIS`.
- Criado manifesto `D:\ISIS_IA\ISIS\config\phase2_structure_manifest.json`.
- Criado relatorio `reports/phase2_structure.md`.
- Adicionado script idempotente `scripts/phase2_create_ssd_structure.py`.
- Adicionado teste da estrutura SSD.

## 0.1.4 - 2026-07-28

- Executada Fase 3 do prompt ISIS.
- Criado backup inicial do `CEREBRO_VIVO`.
- Criado script `scripts/phase3_backup_cerebro_vivo.py`.
- Criado relatorio `reports/phase3_backup.md`.
- Criada documentacao `docs/BACKUP.md`.
- Adicionados testes do backup.

## 0.1.5 - 2026-07-28

- Executada Fase 4 do prompt ISIS.
- Migrado `CEREBRO_VIVO` por copia para `D:\ISIS_IA\ISIS\brain\cerebro_vivo`.
- Validacao SHA-256 concluida para 203112 arquivos.
- Criado manifesto `D:\ISIS_IA\ISIS\logs\migration\migration_manifest.json`.
- Criado relatorio `reports/phase4_migration.md`.
- Criada documentacao `docs/MIGRATION.md`.
- Adicionados testes da migracao.

## 0.1.6 - 2026-07-28

- Executada Fase 5 do prompt ISIS.
- Criado validador `scripts/phase5_validate_migrated_vault.py`.
- Criados relatorios `reports/phase5_validation.md` e `.json`.
- Criada documentacao `docs/OBSIDIAN_INTEGRATION.md`.
- Ajustado teste para nao depender do estado real do Obsidian aberto.
- Adicionados testes de validacao do cofre migrado.

## 0.1.7 - 2026-07-28

- Corrigidos 87 links internos do cofre migrado com regra deterministica.
- Criado backup dos arquivos alterados em `D:\ISIS_IA\ISIS\backups\manual\phase5_link_remediation_20260728_163249`.
- Criado script `scripts/phase5_remediate_links.py`.
- Executada Fase 6.
- Criada configuracao central `D:\ISIS_IA\ISIS\config\isis_config.json`.
- Atualizado `D:\ISIS_IA\AURORA\data\config.json`.
- Criada documentacao `docs/CONFIGURATION_CENTRAL.md`.
- Adicionados testes da configuracao central.

## 0.1.8 - 2026-07-28

- Executada Fase 7 do prompt ISIS.
- Criado nucleo `IsisAssistantCore`.
- Criados `EventBus`, `CommandRouter`, `ToolRegistry` e `HealthMonitor`.
- Adicionado comando CLI `python -m aurora.cli core`.
- Criada documentacao `docs/CORE.md`.
- Adicionados testes do nucleo.

## 0.1.9 - 2026-07-28

- Executada Fase 8 do prompt ISIS.
- Criada camada `aurora.core.model_provider`.
- Implementados providers Mock, Ollama, llama.cpp e LM Studio.
- Adicionado comando `python -m aurora.cli generate`.
- Detectado Ollama local instalado, sem modelos.
- Detectada GPU RTX 3060 via `nvidia-smi`.
- Criada documentacao `docs/LOCAL_MODELS.md`.
- Adicionados testes da camada de modelos.

## 0.2.0 - 2026-07-28

- Executada Fase 9 do prompt ISIS.
- Criado `aurora.core.project_memory`.
- Criado indice SQLite `D:\ISIS_IA\ISIS\data\databases\project_memory.sqlite`.
- Indexados 83194 arquivos Markdown do CEREBRO VIVO migrado.
- Adicionado comando `python -m aurora.cli index-obsidian`.
- Adicionado comando `python -m aurora.cli project-search`.
- Criada documentacao `docs/PROJECT_MEMORY.md`.
- Adicionados testes de memoria de projetos.

## 0.2.1 - 2026-07-28

- Executada Fase 10 do prompt ISIS.
- Criado pacote `aurora.integrations`.
- Criado conector Obsidian READ_ONLY.
- Criado banco `D:\ISIS_IA\ISIS\data\databases\obsidian_readonly.sqlite`.
- Extraidos YAML simples, tags, links, backlinks e checklists.
- Criado script `scripts/phase10_obsidian_readonly.py`.
- Criada documentacao `docs/OBSIDIAN_READONLY.md`.
- Adicionados testes do conector Obsidian.

## 0.2.2 - 2026-07-28

- Executada Fase 11 do prompt ISIS.
- Criado `aurora.core.hybrid_search`.
- Adicionado comando `python -m aurora.cli search`.
- Criada documentacao `docs/HYBRID_SEARCH.md`.
- Criado relatorio `reports/phase11_hybrid_search.md`.
- Adicionados testes da busca hibrida.

## 0.2.3 - 2026-07-28

- Executada Fase 12 do prompt ISIS.
- Criado `aurora.core.project_catalog`.
- Criado banco `D:\ISIS_IA\ISIS\data\databases\project_catalog.sqlite`.
- Consolidados 29 projetos/candidatos.
- Adicionados comandos `consolidate-projects` e `projects`.
- Criada documentacao `docs/PROJECT_CATALOG.md`.
- Criado relatorio `reports/phase12_project_catalog.md`.
- Adicionados testes do catalogo de projetos.

## 0.2.4 - 2026-07-28

- Executada Fase 13 do prompt ISIS.
- Criado `aurora.core.knowledge_records`.
- Criado banco `D:\ISIS_IA\ISIS\data\databases\knowledge_records.sqlite`.
- Importadas 1080 decisoes e 10612 bugs.
- Adicionados comandos `import-knowledge-records`, `decisions` e `bugs`.
- Criada documentacao `docs/KNOWLEDGE_RECORDS.md`.
- Criado relatorio `reports/phase13_knowledge_records.md`.
- Adicionados testes de decisoes e bugs.

## 0.2.5 - 2026-07-28

- Executada Fase 14 do prompt ISIS.
- Criada factory `aurora.voice.factory`.
- Conectada voz ao `IsisAssistantCore`.
- Adicionado comando `python -m aurora.cli voice-core`.
- Criada documentacao `docs/VOICE_CORE.md`.
- Adicionados testes de voz conectada ao nucleo.

## 0.2.6 - 2026-07-28

- Executada Fase 15 do prompt ISIS.
- Criado `aurora.core.security`.
- Implementado `SecurityGuard`.
- Conectada ferramenta `security_status` ao nucleo.
- Adicionado comando `python -m aurora.cli security-status`.
- Criada documentacao `docs/SECURITY_GUARD.md`.
- Adicionados testes de seguranca.

## 0.2.7 - 2026-07-28

- Executada Fase 16 do prompt ISIS.
- Criado pacote `aurora.perception`.
- Implementada visao de tela manual/mock com politica de privacidade.
- Adicionada redacao de senha, token, CPF e cartao.
- Adicionados comandos `screen-status` e `screen-mock`.
- Criada documentacao `docs/SCREEN_VISION.md`.
- Adicionados testes da visao de tela segura.

## 0.2.8 - 2026-07-28

- Executada Fase 17 do prompt ISIS.
- Criado pacote `aurora.automation`.
- Implementado planejamento de acoes de UI.
- Implementada politica de aprovacao por acao.
- Adicionado executor mock sem interacao real com Windows.
- Adicionados comandos `ui-plan` e `ui-mock-action`.
- Criada documentacao `docs/UI_AUTOMATION.md`.
- Adicionados testes da automacao controlada.

## 0.2.9 - 2026-07-28

- Executada Fase 18 do prompt ISIS.
- Criada ponte `aurora.automation.screen_bridge`.
- Conectada analise de tela mock a sugestoes de UI.
- Baixa confianca agora bloqueia execucao.
- Adicionado comando `screen-ui-suggest`.
- Criada documentacao `docs/SCREEN_AUTOMATION_BRIDGE.md`.
- Adicionados testes da ponte tela/automacao.

## 0.3.0 - 2026-07-28

- Executada Fase 19 do prompt ISIS.
- Criado `aurora.automation.action_audit`.
- Adicionada auditoria JSONL para acoes de UI mock/bloqueadas.
- Adicionado comando `ui-permissions-status`.
- Adicionado comando `ui-action-audit`.
- Ajustado custo do `coding-local-mock` para evitar fallback por VRAM real.
- Criada documentacao `docs/ACTION_AUDIT.md`.
- Adicionados testes de auditoria de acoes.

## 0.3.1 - 2026-07-28

- Executada Fase 20 do prompt ISIS.
- Criado pacote `aurora.ui`.
- Implementado snapshot local de status/permissoes/memoria.
- Implementada UI Tkinter local.
- Adicionados comandos `ui-snapshot` e `ui-dashboard`.
- Criada documentacao `docs/LOCAL_DASHBOARD.md`.
- Adicionados testes do dashboard local.

## 0.3.2 - 2026-07-28

- Executada Fase 21 do prompt ISIS.
- Criado `aurora.core.auth`.
- Implementada autenticacao local com PBKDF2-SHA256.
- Adicionados comandos `auth-status`, `auth-bootstrap` e `profile-set`.
- Troca de perfil exige validacao por variavel de ambiente.
- Criada documentacao `docs/LOCAL_AUTH.md`.
- Adicionados testes da autenticacao local.

## 0.3.3 - 2026-07-28

- Executada Fase 22 do prompt ISIS.
- Criado `aurora.ui.privileges`.
- Adicionados controles editaveis de perfil na UI local.
- Adicionado comando `ui-privileges-status`.
- UI solicita senha em memoria e nao armazena segredo.
- Criada documentacao `docs/PRIVILEGE_UI.md`.
- Adicionados testes dos controles de privilegio.

## 0.3.4 - 2026-07-28

- Executada Fase 23 do prompt ISIS.
- Criado `aurora.core.privilege_audit`.
- Adicionada auditoria JSONL de mudancas/tentativas de privilegio.
- Adicionado botao de emergencia na UI local.
- Adicionados comandos `emergency-stop` e `privilege-audit`.
- Criada documentacao `docs/PRIVILEGE_AUDIT.md`.
- Adicionados testes de emergencia e auditoria.

## 0.3.5 - 2026-07-28

- Executada Fase 24 do prompt ISIS.
- Criado `aurora.ui.skills_panel`.
- Adicionada aba `Skills` ao dashboard local.
- Adicionados comandos `ui-skills-snapshot` e `ui-skill-run`.
- Execucao de habilidade passa por autorizacao e sandbox.
- Criada documentacao `docs/SKILLS_PANEL.md`.
- Adicionados testes do painel de habilidades.

## 0.3.6 - 2026-07-28

- Executada Fase 25 do prompt ISIS.
- Criado `aurora.ui.memory_panel`.
- Adicionada listagem de memorias locais na UI.
- Adicionados comandos `ui-memory-propose`, `ui-memory-list` e `ui-memory-status`.
- Registros novos entram como `PROPOSED`.
- Criada documentacao `docs/MEMORY_PANEL.md`.
- Adicionados testes do painel de memoria.

## 0.3.7 - 2026-07-28

- Executada Fase 26 do prompt ISIS.
- Criado `aurora.core.memory_audit`.
- Adicionada auditoria JSONL de proposta/aprovacao/rejeicao de memoria.
- Adicionados botoes `Confirm` e `Reject` na aba `Memory`.
- Adicionado comando `memory-approval-audit`.
- Reduzido custo dos modelos mock para roteamento deterministico sob baixa VRAM real.
- Criada documentacao `docs/MEMORY_APPROVAL_AUDIT.md`.
- Adicionados testes da auditoria de memoria.

## 0.3.8 - 2026-07-28

- Executada Fase 27 do prompt ISIS.
- Adicionados filtros de status na aba `Memory`.
- Adicionada exportacao local de memoria em JSON/Markdown.
- Adicionado comando `ui-memory-export`.
- Criada documentacao `docs/MEMORY_EXPORT.md`.
- Adicionados testes de exportacao de memoria.

## 0.3.9 - 2026-07-28

- Executada Fase 28 do prompt ISIS.
- Criado `aurora.core.audit_report`.
- Adicionado relatorio consolidado de auditoria local.
- Adicionado comando `audit-report`.
- Criada documentacao `docs/AUDIT_REPORT.md`.
- Adicionados testes do relatorio de auditoria.

## 0.4.0 - 2026-07-28

- Executada Fase 29 do prompt ISIS.
- Criado `aurora.core.report_integrity`.
- Adicionado manifesto SHA-256 para relatorios locais.
- Adicionados comandos `report-integrity` e `report-integrity-verify`.
- Criada documentacao `docs/REPORT_INTEGRITY.md`.
- Adicionados testes de integridade de relatorios.

## 0.4.1 - 2026-07-28

- Executada Fase 30 do prompt ISIS.
- Criado `aurora.core.local_signature`.
- Adicionada assinatura local HMAC-SHA256 de relatorios.
- Adicionados comandos `signature-key-status`, `sign-report` e `verify-signature`.
- Criada documentacao `docs/LOCAL_SIGNATURE.md`.
- Adicionados testes de assinatura local.

## 0.4.2 - 2026-07-28

- Executada Fase 31 do prompt ISIS.
- Adicionado status detalhado da chave de assinatura.
- Adicionada rotacao local com backup previo.
- Adicionado comando `signature-key-rotate`.
- Criada documentacao `docs/SIGNATURE_KEY_ROTATION.md`.
- Adicionados testes de rotacao da chave.

## 0.4.3 - 2026-07-28

- Executada Fase 32 do prompt ISIS.
- Criado `aurora.core.key_acl`.
- Adicionada inspecao nao destrutiva de ACL da chave local.
- Adicionado comando `signature-key-acl-status`.
- Criada documentacao `docs/KEY_ACL.md`.
- Adicionados testes da inspecao de ACL.

## 0.4.4 - 2026-07-28

- Executada Fase 33 do prompt ISIS.
- Adicionada aplicacao controlada de ACL restrita com dry-run por padrao.
- Adicionado rollback via backup `icacls`.
- Adicionados comandos `signature-key-acl-apply` e `signature-key-acl-rollback`.
- Criada documentacao `docs/KEY_ACL_APPLY.md`.
- Adicionados testes do fluxo de ACL.

## 0.4.5 - 2026-07-28

- Executada Fase 34 do prompt ISIS.
- Aplicada ACL operacional restrita na chave de assinatura.
- Removida heranca de ACL do arquivo da chave.
- Validada assinatura apos aplicacao.
- Criada documentacao `docs/KEY_ACL_OPERATIONAL.md`.

## 0.4.6 - 2026-07-28

- Executada Fase 35 do prompt ISIS.
- Criado `aurora.ui.audit_panel`.
- Adicionada aba `Audit` ao dashboard.
- Adicionado comando `ui-audit-snapshot`.
- Criada documentacao `docs/AUDIT_PANEL.md`.
- Adicionados testes do painel de auditoria.

## 0.4.7 - 2026-07-28

- Executada Fase 36 do prompt ISIS.
- Criado `aurora.core.report_maintenance`.
- Adicionado comando `reports-regenerate`.
- Adicionado botao `Regenerate reports` na aba `Audit`.
- Criada documentacao `docs/REPORT_MAINTENANCE.md`.
- Adicionados testes de manutencao de relatorios.

## 0.4.8 - 2026-07-28

- Executada Fase 37 do prompt ISIS.
- Adicionado historico JSONL de regeneracao de relatorios.
- Adicionado comando `reports-history`.
- Criada documentacao `docs/REPORT_HISTORY.md`.
- Adicionados testes do historico de relatorios.

## 0.4.9 - 2026-07-28

- Executada Fase 38 do prompt ISIS.
- Aba `Audit` agora mostra contagem de historico de relatorios.
- Aba `Audit` mostra horario da ultima regeneracao.
- Corrigido manifesto de integridade para ignorar arquivos `*.sig.json`.
- Criada documentacao `docs/AUDIT_HISTORY_PANEL.md`.
- Adicionados testes do historico no painel.

## 0.5.0 - 2026-07-28

- Executada Fase 39 operacional de modelos locais.
- Baixados `qwen2.5-coder:14b`, `llama3.1:8b`, `nomic-embed-text:latest` e `deepseek-r1:8b`.
- Migrado runtime Ollama para `D:\ISIS_IA\ISIS\runtime\ollama`.
- Configurado armazenamento Ollama em `D:\ISIS_IA\ISIS\models\ollama`.
- Baixado `Ternary-Bonsai-27B-Q2_0.gguf` para `D:\ISIS_IA\ISIS\models\huggingface`.
- Conectado `OllamaModelProvider` ao nucleo antes do fallback mock.
- Atualizadas rotas reais de modelo em `data/config.json`.
- Atualizada documentacao `docs/LOCAL_MODELS.md`.
- Criada documentacao `docs/TERNARY_BONSAI_27B.md`.

## 0.5.1 - 2026-07-28

- Executada Fase 40 de embeddings reais de memoria.
- Criado `aurora.core.embeddings`.
- Adicionado banco `memory_embeddings.sqlite`.
- Adicionados comandos `memory-embed` e `memory-semantic-search`.
- Integrado `nomic-embed-text:latest` via Ollama local.
- Criada documentacao `docs/MEMORY_EMBEDDINGS.md`.

## 0.5.2 - 2026-07-28

- Instalado runtime local `llama.cpp` b10173 CUDA 12.4.
- Registrado status operacional do `Ternary-Bonsai-27B-Q2_0.gguf`.
- Baixado `KAT-Coder-V2.5-Dev` completo do Hugging Face.
- Criado `data/external_models.json`.
- Criado `scripts/hf_models_status.ps1`.
- Criada documentacao `docs/KAT_CODER_V2_5_DEV.md`.

## 0.5.3 - 2026-07-28

- Baixado `qwen3-coder:30b` via Ollama.
- Configurado `qwen3-coder:30b` como prioridade 1 para perfil `CODING`.
- Mantido `qwen2.5-coder:14b` como fallback.
- Removido KAT-Coder local por solicitacao do usuario.
- Atualizado registro `data/external_models.json`.

## 0.5.4 - 2026-07-28

- Executada Fase 43 de embeddings do indice de projetos.
- Adicionado `ProjectEmbeddingIndex`.
- Adicionados comandos `project-embed` e `project-semantic-search`.
- Criado banco `project_note_embeddings.sqlite`.
- Criada documentacao `docs/PROJECT_EMBEDDINGS.md`.

## 0.5.5 - 2026-07-28

- Executada Fase 44 de fila e progresso de embeddings.
- `project-embed` agora avanca por notas pendentes.
- Adicionado comando `project-embed-progress`.
- Adicionado comando `project-embed-batch`.
- Criada documentacao `docs/PROJECT_EMBEDDING_BATCH.md`.

## 0.5.6 - 2026-07-28

- Executada Fase 45 de worker de embeddings.
- Adicionado comando `project-embed-worker`.
- Adicionado comando `project-embed-history`.
- Criado historico `project_embedding_worker.jsonl`.
- Criada documentacao `docs/PROJECT_EMBEDDING_WORKER.md`.

## 0.5.7 - 2026-07-28

- Executada Fase 46 de interface HUD.
- Criado `aurora.ui.hud_dashboard`.
- Adicionado comando `ui-hud`.
- Adicionado comando `ui-hud-snapshot`.
- Criada documentacao `docs/HUD_INTERFACE.md`.

## 0.5.8 - 2026-07-28

- Executada Fase 47 de voz real com Piper.
- Baixado runtime Piper Windows.
- Baixada voz `pt_BR-faber-medium`.
- Configurado `tts_engine=piper`.
- Adicionados comandos `voice-status` e `voice-speak`.
- HUD agora mostra status de voz e botao `VOZ TESTE`.
- Criada documentacao `docs/VOICE_PIPER_REAL.md`.

## 0.5.9 - 2026-07-28

- Executada Fase 48 de HUD operacional.
- HUD Tkinter agora envia prompts reais ao core.
- HUD Tkinter mantém historico de conversa e fala respostas via Piper.
- Criado servidor web local `ui-hud-web`.
- Link local de teste: `http://127.0.0.1:8765/`.
- Adicionados endpoints `/api/snapshot`, `/api/chat`, `/api/voice-test` e `/api/audio`.
- Atualizada documentacao `docs/HUD_INTERFACE.md`.

## 0.6.0 - 2026-07-28

- Aplicado `Development_Framework` ao projeto AURORA.
- Criado `00_MASTER.md`.
- Criado `AGENTS.md`.
- Criada governanca em `docs/framework`.
- Registrado HUD web oficial em `aurora/ui/hud_web.py`.
- Registrada voz feminina oficial `dii_pt-BR`.
- Criado `.gitignore` basico.

## 0.6.1 - 2026-07-28

- Melhorado HUD web operacional.
- `MIC` agora usa ditado do navegador em `pt-BR`.
- `VOZ NATURAL` usa voz nativa do Chrome/Windows e Piper como fallback.
- Navegacao lateral agora troca paineis reais.
- `ANEXO` abre seletor local de arquivos.
- `PARAR` cancela voz/ditado e resposta pendente no cliente.

## 0.6.2 - 2026-07-28

- Criada preparacao separada de texto para TTS em `aurora.voice.text`.
- TTS deixa de receber Markdown bruto.
- HUD web preserva `response` na UI e envia `speech_text` limpo para voz natural.
- Piper e TTS mock sanitizam texto imediatamente antes da sintese.

## 0.6.3 - 2026-07-28

- Microfone do HUD web envia automaticamente a transcricao final.
- HUD web bloqueia envio duplicado durante resposta pendente.
- Roteamento de codigo reconhece plural e acento em `codigos/códigos`.
- Roteador deixa de cair em mock apenas por VRAM baixa quando ha RAM suficiente.

## 0.6.4 - 2026-07-28

- Removido backlog bruto de embeddings da conversa inicial.
- HUD mostra mensagem humana de memoria pronta e mantem contadores tecnicos nos paineis.
- Executado lote real de embeddings, avancando para 35 indexadas.

## 0.6.5 - 2026-07-28

- HUD web passou a usar jobs assincronos para geracao.
- Adicionado historico permanente de conversas em SQLite.
- Adicionados projetos locais persistidos em SQLite.
- Sidebar mostra projetos e conversas recentes.
- Adicionados endpoints de conversa, projeto, busca, status e cancelamento.
- Respostas ganharam acoes de copiar, tentar novamente e editar pergunta.

## 0.6.6 - 2026-07-28

- Corrigido footer do HUD web oculto apos respostas longas.
- Campo de comando, `MIC`, `ENVIAR` e `PARAR` permanecem visiveis no desktop.
- HUD devolve foco ao input apos conclusao, cancelamento ou erro do job.

## 0.6.7 - 2026-07-28

- Adicionada arquitetura modular de voz local.
- Adicionado roteador TTS com fallback automatico.
- Piper permanece fallback offline validado.
- Kokoro e Chatterbox adicionados como opcionais aguardando modelo pt-BR validado.
- Adicionados cache de audio, normalizador PT-BR, VAD inicial, interrupcao e fila de fala.
- Adicionados comandos `voice-test`, `voice-cache-clear` e `voice-benchmark`.
- HUD web recebeu diagnostico de voz e limpeza de cache.

## 0.6.8 - 2026-07-28

- Corrigida rolagem da area de conversa do HUD web.
- Mensagens agora sobem em fluxo de chat e `#messages` possui scrollbar propria.
- Conversas carregadas e novas mensagens rolam automaticamente para o final.

## 0.6.9 - 2026-07-28

- Kokoro e Chatterbox deixam de ser stubs sempre indisponiveis.
- Adicionado adaptador TTS por CLI/manifesto local para motores offline compativeis.
- Adicionados campos `kokoro_command`, `kokoro_model_dir`, `kokoro_voice`, `chatterbox_command`, `chatterbox_model_dir` e `chatterbox_voice`.

## 0.7.0 - 2026-07-28

- Adicionado modulo de Internet controlada com pesquisa publica, cache e historico.
- Adicionada Central de Regras e Permissoes com parser, simulacao, perfis, autorizacoes temporarias e bloqueio emergencial.
- Adicionadas protecoes SSRF, dominio, prompt injection inicial e bloqueio de downloads executaveis.
- HUD web ganhou aba `Internet`.

## 0.7.1 - 2026-07-29

- HUD web deixou de usar TTS do Windows/Chrome.
- Botao `VOZ LOCAL` e respostas passam a tocar somente o WAV gerado pelo Piper local.
- Voz local agora usa canal de audio invisivel desbloqueado por interacao do usuario, sem player visivel na conversa.
