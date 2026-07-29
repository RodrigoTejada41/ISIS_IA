# Auditoria de Privilegios

## Estado

- Fase 23 implementada.
- Log JSONL: `D:\ISIS_IA\ISIS\logs\security\privileges.jsonl`.
- Mudancas de perfil bem-sucedidas sao auditadas.
- Tentativas bloqueadas tambem sao auditadas.
- Parada de emergencia reduz perfil para `MEDIUM`.

## CLI

```powershell
python -m aurora.cli emergency-stop
python -m aurora.cli privilege-audit --limit 20
```

## Regras

- Emergencia nao exige senha.
- Emergencia salva perfil `MEDIUM`.
- Perfil `TOTAL` ainda exige autenticacao local.
- Segredos nao sao gravados no log.

## Pendente

- Motivo manual da emergencia.
- Retorno temporario ao perfil anterior.
- Contador de tentativas invalidas.
