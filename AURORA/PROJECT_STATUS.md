# Estado Inicial e Atual

## Estado inicial registrado

Data: 2026-07-28.

- Workspace: `D:\ISIS_IA`.
- Nao havia repositorio Git.
- Nao havia `README.md`.
- Nao havia pasta `docs`.
- Nao havia codigo AURORA localizavel.
- Nao havia testes.
- Baseline: `python -m pytest` coletou 0 testes.

## Estado atual

- Projeto criado em `D:\ISIS_IA\AURORA`.
- Nucleo funcional com testes automatizados.
- Modelos locais reais instalados via Ollama e conectados ao nucleo.
- UI ainda nao implementada.

## Fase 1 ISIS

- Pasta atual analisada: `D:\ISIS_IA\AURORA`.
- Cofre CEREBRO VIVO detectado: `E:\Projetos\CEREBRO_VIVO`.
- SSD provavel/destino: `D:\ISIS_IA`, com cerca de 239 GB livres.
- Origem provavel/HD: `E:`.
- Relatorio: `D:\ISIS_IA\AURORA\reports\phase1_audit.md`.
- Nenhum arquivo do cofre foi movido, apagado ou modificado.

## Fase 2 ISIS

- Estrutura criada: `D:\ISIS_IA\ISIS`.
- Manifesto: `D:\ISIS_IA\ISIS\config\phase2_structure_manifest.json`.
- Relatorio: `D:\ISIS_IA\AURORA\reports\phase2_structure.md`.
- Diretorios criados: 46.
- Reserva minima validada: 40 GB.
- Nenhum arquivo do CEREBRO VIVO foi copiado, movido, apagado ou modificado.

## Fase 3 ISIS

- Backup inicial: `D:\ISIS_IA\ISIS\backups\manual\cerebro_vivo_backup_20260728_153131`.
- Manifesto: `D:\ISIS_IA\ISIS\backups\manual\cerebro_vivo_backup_20260728_153131\backup_manifest.json`.
- Log: `D:\ISIS_IA\ISIS\logs\migration\phase3_backup_20260728_153131.log`.
- Arquivos origem/destino: 203112.
- Bytes origem/destino: 5286560147.
- Validacao: contagem e tamanho.
- Hash completo: pendente para fase de validacao/migracao.

## Fase 4 ISIS

- Destino migrado: `D:\ISIS_IA\ISIS\brain\cerebro_vivo`.
- Manifesto: `D:\ISIS_IA\ISIS\logs\migration\migration_manifest.json`.
- Log: `D:\ISIS_IA\ISIS\logs\migration\phase4_migration_20260728_153953.log`.
- Relatorio: `D:\ISIS_IA\AURORA\reports\phase4_migration.md`.
- Arquivos origem/destino: 203112.
- Bytes origem/destino: 5286560147.
- Hashes SHA-256 iguais: 203112.
- Origem original preservada: `E:\Projetos\CEREBRO_VIVO`.
- Obsidian ainda nao foi apontado para o novo local.

## Fase 5 ISIS

- Cofre validado: `D:\ISIS_IA\ISIS\brain\cerebro_vivo`.
- Relatorio: `D:\ISIS_IA\AURORA\reports\phase5_validation.md`.
- Status: `warning`.
- Integridade da migracao: valida.
- `.obsidian`: presente.
- Anexos: 2601; vazios: 0.
- Plugins configurados: 0.
- Links verificados: 170934.
- Links nao resolvidos na amostra: 200.
- Nenhuma nota foi alterada.

## Correcao controlada de riscos

- Relatorio: `D:\ISIS_IA\AURORA\reports\phase5_link_remediation.md`.
- Arquivos alterados: 1.
- Links corrigidos: 87.
- Backup previo: `D:\ISIS_IA\ISIS\backups\manual\phase5_link_remediation_20260728_163249`.
- Links restantes: mantidos como pendencia por falta de alvo comprovavel.

## Fase 6 ISIS

- Configuracao central: `D:\ISIS_IA\ISIS\config\isis_config.json`.
- Configuracao do codigo: `D:\ISIS_IA\AURORA\data\config.json`.
- Cofre Obsidian: `D:\ISIS_IA\ISIS\brain\cerebro_vivo`.
- Modo Obsidian: `READ_ONLY`.
- Offline: ativo.
- Internet/tela/camera/microfone: desativados por padrao.
- Perfil: `CONTROLLED`.

## Fase 7 ISIS

- Nucleo: `aurora.core.assistant.IsisAssistantCore`.
- Eventos: `aurora.core.events.EventBus`.
- Comandos: `aurora.core.commands.CommandRouter`.
- Ferramentas: `aurora.core.tools.ToolRegistry`.
- Health check: `aurora.core.health.HealthMonitor`.
- CLI: `python -m aurora.cli core status`.
- Obsidian permanece `READ_ONLY`.
- Modelos ainda so sao roteados, nao executados.

## Fase 8 ISIS

- Camada de modelos: `aurora.core.model_provider`.
- Providers: Mock, Ollama, llama.cpp, LM Studio.
- CLI: `python -m aurora.cli generate`.
- Ollama instalado: sim.
- Modelos Ollama instalados: nenhum.
- GPU detectada: NVIDIA GeForce RTX 3060, 12288 MB.
- VRAM livre na verificacao: 10490 MB.
- Nenhum modelo foi baixado.

## Fase 9 ISIS

- Indice: `D:\ISIS_IA\ISIS\data\databases\project_memory.sqlite`.
- Markdown indexados: 83194.
- Categorias principais: DOCUMENTATION 67653, BUG 10612, TASK 3551, DECISION 1080.
- CLI: `python -m aurora.cli index-obsidian`.
- CLI: `python -m aurora.cli project-search ISIS`.
- Embeddings ainda pendentes.

## Fase 10 ISIS

- Conector Obsidian READ_ONLY: `aurora.integrations.obsidian`.
- Banco: `D:\ISIS_IA\ISIS\data\databases\obsidian_readonly.sqlite`.
- Notas escaneadas: 83194.
- Checklists: 48624.
- Checklists concluidos: 289.
- Backlinks calculados no banco.
- Nenhuma nota alterada.

## Fase 11 ISIS

- Busca hibrida: `aurora.core.hybrid_search.HybridSearchService`.
- CLI: `python -m aurora.cli search ISIS --limit 5`.
- Fontes: `project_memory.sqlite` + `obsidian_readonly.sqlite`.
- Score auditavel por metadados.
- Sem embeddings e sem internet.

## Fase 12 ISIS

- Catalogo: `D:\ISIS_IA\ISIS\data\databases\project_catalog.sqlite`.
- Projetos/candidatos: 29.
- CLI: `python -m aurora.cli consolidate-projects --min-notes 5`.
- CLI: `python -m aurora.cli projects --limit 20`.
- Observacao: agregadores ainda aparecem como candidatos, nao confirmados.

## Fase 13 ISIS

- Banco: `D:\ISIS_IA\ISIS\data\databases\knowledge_records.sqlite`.
- Decisoes importadas: 1080.
- Bugs importados: 10612.
- CLI: `python -m aurora.cli decisions ISIS`.
- CLI: `python -m aurora.cli bugs ISIS`.
- Observacao: registros ainda sao heuristica inicial.

## Fase 14 ISIS

- Voz conectada ao nucleo.
- CLI: `python -m aurora.cli voice-core --transcript "status"`.
- STT/TTS default: mock.
- Microfone real: desativado por padrao.
- Audio mock: `D:\ISIS_IA\ISIS\data\temporary\tts_mock.wav`.

## Fase 15 ISIS

- Guard: `aurora.core.security.SecurityGuard`.
- CLI: `python -m aurora.cli security-status`.
- Pastas permitidas: `D:\ISIS_IA`.
- Pastas protegidas: `C:\Users`.
- Comandos bloqueados: `format`, `diskpart`, `reg delete`.

## Fase 16 ISIS

- Visao de tela: `aurora.perception.screen`.
- CLI: `python -m aurora.cli screen-status`.
- CLI: `python -m aurora.cli screen-mock --text "Campo login"`.
- Modo atual: manual/mock.
- Captura real de tela: desativada.
- Captura continua: desativada.
- Armazenamento de imagens: desativado.
- Redacao de dados sensiveis: ativa.

## Fase 17 ISIS

- Automacao de UI: `aurora.automation.ui`.
- CLI: `python -m aurora.cli ui-plan "salvar formulario"`.
- CLI: `python -m aurora.cli ui-mock-action "salvar formulario" --approve`.
- Executor real: desativado.
- Aprovacao por acao: obrigatoria.
- Alvos/valores sensiveis: bloqueados por politica.

## Fase 18 ISIS

- Ponte tela/automacao: `aurora.automation.screen_bridge`.
- CLI: `python -m aurora.cli screen-ui-suggest "salvar" --text "Botao salvar" --approve`.
- OCR real: nao implementado.
- Execucao real: desativada.
- Baixa confianca: bloqueada.
- Execucao aprovada: apenas mock.

## Fase 19 ISIS

- Auditoria de acoes: `aurora.automation.action_audit`.
- Log: `D:\ISIS_IA\ISIS\logs\automation\ui_actions.jsonl`.
- CLI: `python -m aurora.cli ui-permissions-status`.
- CLI: `python -m aurora.cli ui-action-audit --limit 20`.
- Execucao real de UI: desativada.
- Acoes executadas/bloqueadas em mock sao auditadas.
- Testes atuais: 92 passed.

## Fase 20 ISIS

- UI local: `aurora.ui.dashboard`.
- CLI: `python -m aurora.cli ui-snapshot`.
- CLI: `python -m aurora.cli ui-dashboard`.
- Stack: Tkinter nativo.
- Captura real/automacao real/internet: continuam desativadas.
- Abas: status, permissoes e memoria.
- Notas indexadas exibidas: 83194.
- Testes atuais: 94 passed.

## Fase 21 ISIS

- Autenticacao local: `aurora.core.auth`.
- Hash: PBKDF2-SHA256.
- Arquivo: `D:\ISIS_IA\ISIS\config\auth.json`.
- CLI: `python -m aurora.cli auth-status`.
- CLI: `python -m aurora.cli auth-bootstrap`.
- CLI: `python -m aurora.cli profile-set CONTROLLED`.
- Senha nao e armazenada em texto claro.
- Status real: autenticacao ainda nao configurada.
- Testes atuais: 97 passed.

## Fase 22 ISIS

- Controles de privilegio: `aurora.ui.privileges`.
- CLI: `python -m aurora.cli ui-privileges-status`.
- UI: aba `Permissions` com controle de perfil.
- Edicao exige autenticacao local configurada.
- Senha e validada em memoria, sem armazenamento em claro.
- Status real: bloqueado porque `auth.json` ainda nao existe.
- Testes atuais: 100 passed.

## Fase 23 ISIS

- Auditoria de privilegios: `aurora.core.privilege_audit`.
- Log: `D:\ISIS_IA\ISIS\logs\security\privileges.jsonl`.
- CLI: `python -m aurora.cli emergency-stop`.
- CLI: `python -m aurora.cli privilege-audit --limit 20`.
- UI: botao `Emergency stop`.
- Emergencia reduz perfil para `MEDIUM`.
- Status real: perfil atual alterado para `MEDIUM` pelo teste operacional de emergencia.
- Testes atuais: 104 passed.

## Fase 24 ISIS

- Painel de habilidades: `aurora.ui.skills_panel`.
- UI: aba `Skills`.
- CLI: `python -m aurora.cli ui-skills-snapshot`.
- CLI: `python -m aurora.cli ui-skill-run project_list --arg root=D:/ISIS_IA --approve`.
- Execucao usa autorizacao e sandbox existentes.
- Comando `project_list` validado em sandbox.
- Testes atuais: 109 passed.

## Fase 25 ISIS

- Painel de memoria: `aurora.ui.memory_panel`.
- UI: aba `Memory` lista registros locais.
- CLI: `python -m aurora.cli ui-memory-propose "registrar decisao local"`.
- CLI: `python -m aurora.cli ui-memory-list --status PROPOSED`.
- CLI: `python -m aurora.cli ui-memory-status <id> CONFIRMED`.
- Obsidian permanece `READ_ONLY`.
- Teste operacional criado/confirmado: `a80ef97b-1100-4f33-b41c-59bfab7de764`.
- Testes atuais: 113 passed.

## Fase 26 ISIS

- Auditoria de memoria: `aurora.core.memory_audit`.
- Log: `D:\ISIS_IA\ISIS\logs\security\memory_approvals.jsonl`.
- UI: botoes `Confirm` e `Reject` na aba `Memory`.
- CLI: `python -m aurora.cli memory-approval-audit --limit 20`.
- Obsidian permanece `READ_ONLY`.
- Testes atuais: 116 passed.

## Fase 27 ISIS

- UI: filtro de status na aba `Memory`.
- Exportacao: JSON e Markdown.
- CLI: `python -m aurora.cli ui-memory-export D:/ISIS_IA/ISIS/reports/memory_report.json --status CONFIRMED`.
- Obsidian permanece `READ_ONLY`.
- Relatorio operacional: `D:\ISIS_IA\ISIS\reports\memory_report.json`.
- Testes atuais: 119 passed.

## Fase 28 ISIS

- Relatorio de auditoria: `aurora.core.audit_report`.
- CLI: `python -m aurora.cli audit-report D:/ISIS_IA/ISIS/reports/audit_report.json`.
- Fontes: acoes de UI, privilegios e memoria.
- Offline: sem envio externo.
- Relatorio operacional: `D:\ISIS_IA\ISIS\reports\audit_report.json`.
- Testes atuais: 122 passed.

## Fase 29 ISIS

- Integridade de relatorios: `aurora.core.report_integrity`.
- Hash: SHA-256.
- CLI: `python -m aurora.cli report-integrity D:/ISIS_IA/ISIS/reports/report_integrity.json`.
- CLI: `python -m aurora.cli report-integrity-verify D:/ISIS_IA/ISIS/reports/report_integrity.json`.
- Offline: sem assinatura externa.
- Manifesto operacional: `D:\ISIS_IA\ISIS\reports\report_integrity.json`.
- Testes atuais: 125 passed.

## Fase 30 ISIS

- Assinatura local: `aurora.core.local_signature`.
- Algoritmo: HMAC-SHA256.
- Chave: `D:\ISIS_IA\ISIS\config\report_signing_key.json`.
- CLI: `python -m aurora.cli sign-report <file> <signature>`.
- CLI: `python -m aurora.cli verify-signature <file> <signature>`.
- Assinatura operacional: `D:\ISIS_IA\ISIS\reports\report_integrity.sig.json`.
- Testes atuais: 128 passed.

## Fase 31 ISIS

- Rotacao de chave: `aurora.core.local_signature.LocalSignatureService.rotate_key`.
- CLI: `python -m aurora.cli signature-key-status`.
- CLI: `python -m aurora.cli signature-key-rotate`.
- Backup previo criado antes de nova chave.
- ACL Windows restrita ainda pendente.
- Status operacional: chave atual `34f8eff5fa00d700`, backups: 3.
- Testes atuais: 132 passed.

## Fase 32 ISIS

- ACL da chave: `aurora.core.key_acl`.
- CLI: `python -m aurora.cli signature-key-acl-status`.
- Modo: somente leitura, sem aplicar ACL.
- Status operacional: chave existe, mas nao esta restrita por causa de permissao herdada de modificacao.
- Testes atuais: 135 passed.

## Fase 33 ISIS

- Aplicacao ACL: `aurora.core.key_acl.KeyAclManager`.
- CLI: `python -m aurora.cli signature-key-acl-apply`.
- CLI: `python -m aurora.cli signature-key-acl-apply --apply`.
- CLI: `python -m aurora.cli signature-key-acl-rollback <backup> --apply`.
- Padrao seguro: dry-run sem `--apply`.
- Dry-run operacional validado.
- Testes atuais: 138 passed.

## Fase 34 ISIS

- ACL operacional aplicada na chave local.
- Arquivo: `D:\ISIS_IA\ISIS\config\report_signing_key.json`.
- Backup ACL: `D:\ISIS_IA\ISIS\config\report_signing_key_acl_20260728_213216.txt`.
- Status final: `restricted=true`.
- Assinatura verificada: `ok=true`.
- Testes atuais: 138 passed.

## Fase 35 ISIS

- Painel de auditoria: `aurora.ui.audit_panel`.
- UI: aba `Audit`.
- CLI: `python -m aurora.cli ui-audit-snapshot`.
- Mostra eventos de UI, privilegios, memoria, integridade e ACL da chave.
- Snapshot operacional: integridade `true`, chave restrita `true`.
- Testes atuais: 140 passed.

## Fase 36 ISIS

- Manutencao de relatorios: `aurora.core.report_maintenance`.
- CLI: `python -m aurora.cli reports-regenerate`.
- UI: botao `Regenerate reports` na aba `Audit`.
- Fluxo: auditoria, integridade, assinatura, verificacao.
- Regeneracao operacional concluida com `signature_ok=true`.
- Testes atuais: 142 passed.

## Fase 37 ISIS

- Historico de relatorios: `D:\ISIS_IA\ISIS\logs\security\report_maintenance.jsonl`.
- CLI: `python -m aurora.cli reports-history --limit 20`.
- Cada regeneracao grava resultado e assinatura.
- Testes atuais: 144 passed.

## Fase 38 ISIS

- UI Audit: contagem do historico de relatorios.
- UI Audit: horario da ultima regeneracao.
- CLI relacionado: `python -m aurora.cli ui-audit-snapshot`.
- Integridade operacional: `true`.
- Chave restrita: `true`.
- Testes atuais: 145 passed.

## Fase 39 ISIS

- Modelos Ollama baixados:
  - `qwen2.5-coder:14b`.
  - `llama3.1:8b`.
  - `nomic-embed-text:latest`.
  - `deepseek-r1:8b`.
- Modelo Hugging Face baixado:
  - `D:\ISIS_IA\ISIS\models\huggingface\prism-ml\Ternary-Bonsai-27B-gguf\Ternary-Bonsai-27B-Q2_0.gguf`.
- Provider real conectado: `OllamaModelProvider`.
- Ordem de providers: Ollama primeiro, mock como fallback.
- Rotas reais em `D:\ISIS_IA\AURORA\data\config.json`.
- Logs de download: `D:\ISIS_IA\ISIS\logs\models`.
- Runtime Ollama migrado para `D:\ISIS_IA\ISIS\runtime\ollama`.
- `OLLAMA_MODELS` do usuario configurado para `D:\ISIS_IA\ISIS\models\ollama`.
- Scripts locais: `scripts\start_ollama_project.ps1` e `scripts\ollama_project_status.ps1`.
- Exclusao das pastas antigas em `C:\Users\Rodrigo Tejada` foi solicitada, mas bloqueada pela politica da sessao.
- Proximo foco tecnico: embeddings reais na memoria permanente.

## Fase 40 ISIS

- Embeddings reais de memoria implementados.
- Modulo: `aurora.core.embeddings`.
- Banco: `D:\ISIS_IA\ISIS\data\databases\memory_embeddings.sqlite`.
- Modelo: `nomic-embed-text:latest` via Ollama local.
- CLI: `python -m aurora.cli memory-embed --limit 100`.
- CLI: `python -m aurora.cli memory-semantic-search "consulta" --limit 5`.
- Conteudo com sensibilidade `HIGH` nao e indexado.
- Idempotencia por SHA-256 do conteudo.
- Validacao real: busca semantica retornou memoria de embeddings locais como primeiro resultado.

## Fase 41 ISIS

- Runtime `llama.cpp` instalado em `D:\ISIS_IA\ISIS\runtime\llama.cpp`.
- `Ternary-Bonsai-27B-Q2_0.gguf` validado por SHA-256.
- Tentativa Ollama: falhou com `tensor "output.weight" size overflow`.
- Tentativa `llama.cpp` b10173: falhou com offset inconsistente em `output_norm.weight`.
- Status Bonsai: baixado, registrado, bloqueado por compatibilidade do runtime/GGUF.
- `KAT-Coder-V2.5-Dev` baixado completo em `D:\ISIS_IA\ISIS\models\huggingface\Kwaipilot\KAT-Coder-V2.5-Dev`.
- Tamanho KAT local: cerca de 64.59 GB.
- Status KAT: baixado e registrado, nao ativo no roteador local por exigir runtime/infra de servidor maior.
- Registro: `D:\ISIS_IA\AURORA\data\external_models.json`.
- Script: `D:\ISIS_IA\AURORA\scripts\hf_models_status.ps1`.

## Fase 42 ISIS

- Modelo compatível escolhido para substituir KAT local: `qwen3-coder:30b`.
- Download Ollama concluído em `D:\ISIS_IA\ISIS\models\ollama`.
- Rota `CODING` atual:
  - prioridade 1: `qwen3-coder:30b`.
  - prioridade 2: `qwen2.5-coder:14b`.
- KAT-Coder removido de `D:\ISIS_IA\ISIS\models\huggingface\Kwaipilot\KAT-Coder-V2.5-Dev`.
- Espaco livre em `D:` apos remocao: cerca de 153.6 GB.
- Validacao real: `python -m aurora.cli generate "corrija este codigo Python em uma linha: print('oi')"` retornou via provider `ollama`, modelo `qwen3-coder:30b`.

## Fase 43 ISIS

- Embeddings reais do indice grande de projetos implementados.
- Modulo: `aurora.core.embeddings.ProjectEmbeddingIndex`.
- Banco: `D:\ISIS_IA\ISIS\data\databases\project_note_embeddings.sqlite`.
- CLI: `python -m aurora.cli project-embed --limit 50`.
- CLI: `python -m aurora.cli project-semantic-search "consulta" --limit 10`.
- Modelo: `nomic-embed-text:latest` via Ollama local.
- Indexacao em lotes, com filtros opcionais por projeto/categoria.
- Obsidian permanece `READ_ONLY`.
- Validacao real: `project-embed --limit 5` indexou 5 notas; busca semantica retornou resultados.

## Fase 44 ISIS

- Fila real de embeddings de projetos implementada.
- `project-embed` agora pula notas ja indexadas e avanca para pendentes.
- CLI: `python -m aurora.cli project-embed-progress`.
- CLI: `python -m aurora.cli project-embed-batch --batch-size 50 --max-batches 4`.
- Progresso real atual apos validacao: 15 de 83194 notas indexadas.
- Pendentes reais apos validacao: 83179.
- Documentacao: `D:\ISIS_IA\AURORA\docs\PROJECT_EMBEDDING_BATCH.md`.

## Fase 45 ISIS

- Worker controlado de embeddings de projetos implementado.
- CLI: `python -m aurora.cli project-embed-worker --batch-size 25 --max-batches 10 --max-seconds 300`.
- CLI: `python -m aurora.cli project-embed-history --limit 20`.
- Historico: `D:\ISIS_IA\ISIS\logs\memory\project_embedding_worker.jsonl`.
- Stop reasons: `max_batches`, `max_seconds`, `no_pending`.
- Progresso real apos validacao: 25 de 83194 notas indexadas.
- Pendentes reais apos validacao: 83169.
- Documentacao: `D:\ISIS_IA\AURORA\docs\PROJECT_EMBEDDING_WORKER.md`.

## Fase 46 ISIS

- Nova interface HUD futurista implementada.
- Modulo: `aurora.ui.hud_dashboard`.
- CLI: `python -m aurora.cli ui-hud`.
- CLI: `python -m aurora.cli ui-hud-snapshot`.
- Layout: topo de status, navegacao lateral, conversa central, painel IA direito, rodape de comando.
- Avatar animado em Canvas.
- Snapshot real validado com modelo `qwen3-coder:30b` e embeddings `nomic-embed-text:latest`.
- Documentacao: `D:\ISIS_IA\AURORA\docs\HUD_INTERFACE.md`.

## Fase 47 ISIS

- TTS real local implementado com Piper.
- Runtime: `D:\ISIS_IA\ISIS\runtime\piper\piper\piper.exe`.
- Voz: `pt_BR-faber-medium`.
- Arquivo de voz: `D:\ISIS_IA\ISIS\voice\piper\voices\pt_BR-faber-medium\pt\pt_BR\faber\medium\pt_BR-faber-medium.onnx`.
- Configuracao `data\config.json`: `tts_engine=piper`.
- CLI: `python -m aurora.cli voice-status`.
- CLI: `python -m aurora.cli voice-speak "texto"`.
- HUD: status de voz e botao `VOZ TESTE`.
- `voice-core` agora gera WAV com Piper mesmo quando a resposta informa bloqueio de politica.
- STT/microfone real permanecem desativados.

## Fase 48 ISIS

- HUD operacional concluida.
- Tkinter: campo de comando envia prompts reais para `IsisAssistantCore`.
- Tkinter: historico real na conversa e resposta por voz Piper quando TTS esta pronto.
- Web local: `python -m aurora.cli ui-hud-web --host 127.0.0.1 --port 8765`.
- Link de teste: `http://127.0.0.1:8765/`.
- Endpoints: `/api/snapshot`, `/api/chat`, `/api/voice-test`, `/api/audio`.
- Servidor validado em `127.0.0.1:8765`.
- Chat validado com `status`; retornou bloqueio seguro por politica e WAV Piper.
- Testes focados da HUD/voz/web: 7 passed.

## Framework de desenvolvimento aplicado

- Framework origem: `D:\ISIS_IA\Development_Framework`.
- Projeto alvo: `D:\ISIS_IA\AURORA`.
- Controle mestre criado: `D:\ISIS_IA\AURORA\00_MASTER.md`.
- Instrucoes de agente criadas: `D:\ISIS_IA\AURORA\AGENTS.md`.
- Pasta de governanca criada: `D:\ISIS_IA\AURORA\docs\framework`.
- HUD web oficial registrado: `D:\ISIS_IA\AURORA\aurora\ui\hud_web.py`.
- Link web oficial da IA: `http://127.0.0.1:8765/`.
- Voz feminina oficial: `dii_pt-BR`.

## HUD web mic/voz/navegacao

- `MIC` usa Web Speech Recognition do navegador em `pt-BR`.
- `VOZ NATURAL` usa `speechSynthesis` do Chrome/Windows e Piper como fallback.
- Menu lateral agora alterna paineis funcionais.
- `ANEXO` abre seletor local de arquivos.
- `PARAR` cancela voz/ditado e resposta pendente no cliente.
- Servidor reiniciado na porta `8765`.
- Validacao focada: 8 passed.

## Correcao TTS Markdown

- Criado `aurora.voice.text.prepare_text_for_speech`.
- UI mantem resposta original; TTS recebe `speech_text` limpo.
- Aplicado em Piper, TTS mock, HUD Tkinter e HUD web `speechSynthesis`.
- Blocos de codigo/JSON/comandos sao resumidos para fala.
- Validacao focada: 13 passed.

## Correcao voz e codigo HUD

- `MIC` agora envia automaticamente a transcricao final.
- Cliente web evita envio duplicado durante uma resposta pendente.
- Roteador reconhece `codigo`, `código`, `codigos` e `códigos`.
- VRAM baixa nao derruba para mock quando ha RAM suficiente.
- Validacao focada: 19 passed.

## Correcao exibicao embeddings no chat

- Removida bolha inicial com backlog bruto de embeddings.
- Chat agora mostra `Memoria local pronta para consulta. Indexacao semantica segue em segundo plano.`
- Contadores tecnicos continuam nos paineis de memoria/status.
- Worker curto executado: indexed 35, pending 83159.
- Validacao focada: 6 passed.

## HUD assincrono, historico e projetos

- Causa do travamento percebido: `/api/chat` fazia geracao + TTS no request HTTP.
- Criado `aurora.core.conversations.ConversationStore`.
- Banco: `D:\ISIS_IA\ISIS\data\databases\hud_conversations.sqlite`.
- Criado `ChatJobManager` com status `analisando`, `gerando`, `voz`, `concluido`, `erro`, `cancelado`.
- Endpoints: `/api/chat`, `/api/chat-status`, `/api/chat-cancel`, `/api/conversations`, `/api/conversation`, `/api/projects`, `/api/search`.
- HUD web mostra projetos/conversas recentes, pesquisa local, novo projeto, copiar, tentar novamente e editar pergunta.
- Validacao focada: 8 passed.
- Validacao HTTP real: job `status` concluiu e salvou conversa com 2 mensagens.

## Correcao footer/input HUD web

- Causa do novo travamento percebido: resposta longa ocultava o footer por combinacao de `min-height:100vh` e `overflow:hidden`.
- HUD desktop agora usa `height:100vh`, linha central `minmax(0,1fr)` e scroll restrito ao workspace.
- Ao concluir, cancelar ou falhar um job, o HUD libera `sending` e devolve foco ao campo de comando.

## Fase 49 ISIS - Voz local modular

- Criado `aurora.voice.voice_manager.VoiceManager`.
- Criado `aurora.voice.voice_router.VoiceRouter`.
- Criados motores TTS modulares em `aurora.voice.tts`.
- Piper `dii_pt-BR` permanece fallback offline validado.
- Kokoro e Chatterbox entram como motores compativeis por comando local ou `tts_manifest.json`; Piper permanece fallback ate haver instalacao configurada.
- Criado cache local de audio por hash.
- Criado normalizador PT-BR complementar para paths, HTTP 200, email, percentuais e temperatura.
- Criados `SpeechQueue`, `InterruptionManager` e `VoiceActivityDetector`.
- CLI: `voice-test`, `voice-cache-clear`, `voice-benchmark`.
- HUD web: diagnostico de voz e limpeza de cache na aba Configuracoes.
- Validacao completa: `167 passed`.

## Correcao rolagem da conversa HUD web

- `#messages` agora possui rolagem vertical propria.
- `#conversa` virou container flex com altura controlada.
- Novas mensagens e conversas carregadas rolam automaticamente para o final.

## Compatibilidade Kokoro/Chatterbox

- Criado adaptador CLI generico para motores TTS locais.
- `kokoro_command` e `chatterbox_command` podem apontar para qualquer sintetizador local que gere WAV.
- Tambem e aceito `tts_manifest.json` no diretorio do motor.

## Fase 50 ISIS - Internet controlada e regras

- Criado `aurora.internet`.
- Criado `aurora.permissions`.
- Pesquisa publica via `duckduckgo_html+bing_html`, sem API paga obrigatoria.
- Protecoes: SSRF, dominio, esquema, porta, sanitizacao de consulta, prompt injection inicial e cache.
- Historico: `D:\ISIS_IA\ISIS\data\databases\research_history.sqlite`.
- Permissoes: `PermissionEngine`, parser de regras, ativacao versionada, perfis, autorizacoes temporarias e bloqueio emergencial.
- HUD web recebeu aba `Internet`.
- CLI recebeu comandos `internet-*`, `rules-*` e `permission-*`.
- Downloads executaveis/scripts sao bloqueados antes de rede.

## Correcao voz local HUD web

- Removido uso de `speechSynthesis` para TTS no HUD.
- `VOZ LOCAL` e respostas usam apenas audio local gerado pelo Piper.
- `MIC` continua usando API do navegador somente para ditado.
- Voz local usa canal de audio invisivel desbloqueado por clique/Enter/MIC, sem player de audio na conversa.
