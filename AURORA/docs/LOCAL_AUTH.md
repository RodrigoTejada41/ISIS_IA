# Autenticacao Local

## Estado

- Fase 21 implementada.
- Hash: PBKDF2-SHA256.
- Senha em texto claro: nao armazenada.
- Entrada de senha: variavel de ambiente `ISIS_ADMIN_PASSWORD`.
- Troca de perfil exige autenticacao.

## CLI

```powershell
python -m aurora.cli auth-status
python -m aurora.cli auth-bootstrap
python -m aurora.cli profile-set CONTROLLED
```

## Arquivo

- `D:\ISIS_IA\ISIS\config\auth.json`

O arquivo contem algoritmo, iteracoes, salt e hash.

## Regras

- A senha deve ter no minimo 12 caracteres.
- Nao passe senha como argumento de comando.
- Nao registre senha em documentacao.
- `profile-set` falha se a variavel de ambiente nao validar.

## Pendente

- Dialogo grafico para autenticacao.
- Rotacao de credencial.
- Bloqueio temporario apos tentativas invalidas.
