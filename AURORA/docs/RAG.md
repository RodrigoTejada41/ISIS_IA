# RAG Local

Fluxo implementado:

1. Recebe pergunta.
2. Busca memorias confirmadas.
3. Filtra expiradas e sensiveis.
4. Monta contexto limitado.
5. Registra IDs usados em auditoria.

Fallback atual: busca textual SQLite.

Futuro:

- embeddings locais via Ollama.
- Qdrant local.
- indexacao de Markdown, TXT, PDF textual e codigo.

## Fase 9

Foi criado indice textual inicial do CEREBRO VIVO para recuperacao por projeto/categoria/tags/titulo.

## Fase 11

Busca hibrida inicial criada sobre memoria de projetos e metadados Obsidian.
Ainda sem embeddings.
