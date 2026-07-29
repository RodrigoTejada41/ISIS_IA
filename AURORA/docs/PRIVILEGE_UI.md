# Controles de Privilegios

## Estado

- Fase 22 implementada.
- UI local possui controle de perfil.
- Edicao depende de autenticacao local configurada.
- Senha e solicitada em memoria pela UI.
- Senha nao e gravada em log, CLI ou documentacao.

## CLI

```powershell
python -m aurora.cli ui-privileges-status
python -m aurora.cli ui-dashboard
```

## Regras

- Sem `auth.json`, controles editaveis ficam bloqueados.
- Perfil invalido e rejeitado.
- Senha invalida nao altera configuracao.
- Alteracao valida chama `runtime.save_config()`.

## Pendente

- Botao de emergencia.
- Duracao temporaria para perfil `TOTAL`.
- Registro auditavel de tentativa de mudanca de perfil.
