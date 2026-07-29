# Seguranca

Perfis:

- `MEDIUM`: leitura e baixo risco; bloqueia/desautoriza destruicao.
- `CONTROLLED`: operacional diario; confirma acoes medias.
- `TOTAL`: amplo, temporario quando configurado, com auditoria e confirmacao reforcada.

Modos:

- `AUTO_ALLOW`
- `ASK_CONFIRMATION`
- `REQUIRE_STRONG_CONFIRMATION`
- `DENY`

Controles:

- Troca de perfil exige autenticacao.
- TOTAL temporario expira.
- Emergencia volta para MEDIUM e bloqueia novas acoes.
- Auditoria nao grava senhas, tokens ou segredos completos.
- Acoes irreversiveis exigem confirmacao especifica.

## Fase 15

`SecurityGuard` implementado para validar pastas permitidas/protegidas, comandos bloqueados e estados de permissao.
