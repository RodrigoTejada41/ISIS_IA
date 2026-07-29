# Decisoes

## 2026-07-28

- Criar `D:\ISIS_IA\AURORA` porque o workspace nao continha projeto AURORA existente.
- Usar Python por compatibilidade com voz local, SQLite, habilidades e testes.
- Implementar fluxo real de dominio com mocks para STT/TTS/wake word.
- Nao baixar modelos automaticamente.
- Nao usar servicos online automaticamente.
- Considerar hardware principal: Ryzen 7 5700, 32 GB RAM, RTX 3060 12 GB VRAM.
- Manter margem de VRAM: limite padrao 10 GB, fallback reporta 9 GB livre quando `nvidia-smi` nao existe.
- Habilidades HIGH/CRITICAL e acoes irreversiveis exigem confirmacao reforcada.
- Adicionar CLI antes de UI grafica para validar operacao local sem dependencias visuais.
- Criar `data/config.json` automaticamente, sem segredos.
- Adaptadores reais de voz devem falhar claramente quando binario/modelo/voz nao existirem.
- Projeto passa a usar nome funcional ISIS; base local atual permanece em `D:\ISIS_IA\AURORA` ate migracao/renomeacao planejada.
- Fase 1 deve ser somente leitura. Migracao do CEREBRO VIVO fica bloqueada ate confirmacao de origem/destino e backup.
- Criar estrutura operacional da ISIS em `D:\ISIS_IA\ISIS`, mantendo `D:\ISIS_IA\AURORA` como base de codigo atual.
- Exigir reserva minima de 40 GB livres antes de criar estrutura no SSD.
- Fazer backup inicial com `robocopy` sem `/MIR`, preservando origem e validando contagem/tamanho antes da migracao.
- Migrar o cofre por copia para `D:\ISIS_IA\ISIS\brain\cerebro_vivo` e validar por SHA-256 antes de qualquer troca no Obsidian.
- Guardar o manifesto completo de hashes em `D:\ISIS_IA\ISIS\logs\migration\migration_manifest.json`.
- Tratar links internos nao resolvidos como pendencia de saneamento, nao como falha de integridade da copia quando hashes e contagens batem.
- Nao corrigir links do Obsidian automaticamente sem aprovacao explicita.
- Com autorizacao do usuario, corrigir somente links Obsidian com alvo existente comprovado e backup previo do arquivo alterado.
- Configuracao central da ISIS deve manter Obsidian em `READ_ONLY` ate nova autorizacao.
- Tela, camera, microfone e internet ficam desativados por padrao na configuracao central.
- Implementar o nucleo como orquestrador fino sobre runtime, event bus, tool registry, command router e health monitor.
- Nesta fase, selecionar modelo nao significa gerar resposta real; chamada LLM local fica para Fase 8.
- Fase 8 usa providers locais e fallback mock. Nenhum modelo e baixado sem autorizacao.
- Ollama instalado sem modelos locais; manter geracao real desativada ate modelo ser instalado.
- Fase 9 cria indice SQLite textual antes de embeddings para validar recuperacao local sem dependencias pesadas.
- A inferencia de projeto por caminho e heuristica nesta fase; refinamento fica para memoria de projetos dedicada.
- Fase 10 implementa parser YAML simples local para evitar dependencia extra; casos complexos ficam preservados como texto/pendencia.
- Backlinks sao calculados no indice da ISIS, sem escrever no cofre.
- Fase 11 implementa score hibrido simples e auditavel antes de BM25/vetor para manter dependencia zero.
- Fase 12 grava catalogo separado de projetos/candidatos, sem tratar heuristica como confirmacao definitiva.
- Fase 13 importa decisoes/bugs por categoria heuristica com IDs estaveis; revisao humana ainda e necessaria para base final.
