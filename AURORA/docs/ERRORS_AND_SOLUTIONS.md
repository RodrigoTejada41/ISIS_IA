# Erros e Solucoes

## Baseline sem testes

Problema: `python -m pytest` em `D:\ISIS_IA` coletou 0 testes e retornou codigo 1.

Solucao: criar estrutura AURORA com `pyproject.toml` e testes em `AURORA/tests`.

## Aviso de limpeza do pytest em `%TEMP%`

Problema: primeira execucao em `AURORA` passou, mas exibiu `PermissionError` ao limpar `pytest-current` no temp do usuario.

Solucao: repetir validacao final com `TMP` e `TEMP` apontando para pasta temporaria dentro do projeto.

## Auditoria completa do CEREBRO VIVO excedeu timeout

Problema: varredura Python completa de `E:\Projetos\CEREBRO_VIVO` excedeu 120s.

Solucao: implementar auditor com limite de tempo/arquivos, ignorar diretorios tecnicos e complementar totais com `robocopy /L`, que lista sem copiar.

## Criacao da estrutura SSD deve ser idempotente

Problema: repetir a Fase 2 poderia gerar erro ou sobrescrever evidencias.

Solucao: script `phase2_create_ssd_structure.py` cria apenas diretorios ausentes e registra existentes no manifesto.

## `robocopy` retorna codigo 1 em backup valido

Problema: `robocopy` usa codigos diferentes de zero para sucesso parcial/arquivos copiados.

Solucao: tratar codigos `0..7` como sucesso e validar contagem/tamanho de origem e destino.

## Backup contem arquivo extra de manifesto

Problema: backup manual passou a ter um arquivo a mais apos salvar `backup_manifest.json`.

Solucao: na Fase 4, comparar origem com destino migrado por hashes, e tratar backup como evidencia usada, nao como origem de comparacao exata apos manifesto.

## Validador de links gerou falso positivo para pasta relativa

Problema: links como `[[../03_SNIPPETS|Snippets]]` apontavam para pastas existentes, mas eram marcados como ausentes.

Solucao: ajustar `phase5_validate_migrated_vault.py` para aceitar caminhos relativos, pastas e variante `.md`.

## Links Obsidian nao resolvidos no cofre

Problema: amostra de 5000 Markdown encontrou 200 links nao resolvidos, principalmente em `00_PAINEL\README.md` com tokens `QX...`.

Solucao: registrar como pendencia. Nao corrigir automaticamente sem aprovacao.

## Correcao segura de links precisa ser deterministica

Problema: parte dos links quebrados tinha alvos gerados com `QX` ou placeholders, mas muitos nao tinham destino verificavel.

Solucao: corrigir apenas 87 links cujo novo alvo existia. Links sem alvo comprovavel permaneceram como `warning`.

## Scripts executados diretamente precisam ajustar `sys.path`

Problema: `phase5_remediate_links.py` e `phase6_configure_isis.py` falharam quando chamados diretamente por `python scripts\...`.

Solucao: inserir a raiz do projeto em `sys.path` no inicio dos scripts.

## CLI falhou serializando dataclass com slots

Problema: `CommandResult` usa `slots`, portanto nao possui `__dict__`.

Solucao: serializar com `dataclasses.asdict`.

## Ollama instalado sem modelos

Problema: `ollama list` nao retornou modelos instalados.

Solucao: manter `MockModelProvider` como fallback testavel. Download de modelo exige aprovacao explicita.

## Inferencia de projeto ampla no cofre

Problema: o cofre contem codigo, dependencias e exportacoes; inferir projeto pelo primeiro diretorio gera muitos nomes.

Solucao: manter como indice inicial e refinar regras na fase de memoria de projetos dedicada.

## Frontmatter YAML variado quebrou parser simples

Problema: alguns arquivos tinham lista YAML abaixo de chave vazia; o parser tentou adicionar item em valor booleano/string.

Solucao: quando uma linha `  - item` aparece, converter a chave atual para lista antes de adicionar.

## Busca filtrada por projeto retornava metadados sem projeto

Problema: resultados do banco Obsidian nao possuem campo de projeto consolidado e vazavam em busca filtrada.

Solucao: quando houver filtro de projeto/categoria, usar apenas `project_memory` ate consolidar projetos.

## Catalogo inclui agregadores como projetos

Problema: nomes como `projetos`, `historico` e `Logs` sao agregadores do cofre, mas tambem aparecem como candidatos.

Solucao: marcar resultado como catalogo de candidatos e exigir confirmacao/refino posterior antes de tratar como projeto oficial.

## Decisoes e bugs importados por heuristica podem conter ruido

Problema: categoria `BUG` ou `DECISION` vem de classificacao automatica simples.

Solucao: armazenar como registros consultaveis iniciais, com origem preservada e revisao futura obrigatoria.
