# Roteamento de Modelos

Perfis:

- `GENERAL`
- `FAST`
- `REASONING`
- `CODING`
- `VISION`
- `EMBEDDING`
- `SUMMARIZATION`
- `CLASSIFICATION`

Regras deterministicas iniciais:

- Imagem: `VISION`.
- Codigo ou pedido de programacao: `CODING`.
- Memoria: `EMBEDDING`.
- Resumo: `SUMMARIZATION`.
- Prompt curto: `FAST`.
- Contexto longo: `REASONING`.
- Caso geral: `GENERAL`.

Fallback:

1. Perfil escolhido.
2. `GENERAL`.
3. Indisponibilidade clara.

Auditoria registra tarefa, perfil, modelo, motivo, disponibilidade, fallback e recursos.
