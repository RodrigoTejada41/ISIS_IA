# Memoria

Tipos:

- sessao
- conversa
- preferencias
- fatos confirmados
- conhecimento de projetos
- procedimentos
- habilidades
- erros e solucoes
- temporarias
- sensiveis

Estados:

- `PROPOSED`
- `CONFIRMED`
- `REJECTED`
- `EXPIRED`
- `ARCHIVED`

Persistencia atual: SQLite local.

Busca atual: textual com filtro de status, expiracao e sensibilidade.

Regra: inferencia do modelo nao vira fato confirmado sem confirmacao.

## Fase 9

Memoria de projetos indexada em `D:\ISIS_IA\ISIS\data\databases\project_memory.sqlite`.

Fonte: cofre migrado em modo `READ_ONLY`.
