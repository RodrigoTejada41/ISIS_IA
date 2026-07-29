# Instrucoes para agentes - AURORA / ISIS

## Antes de trabalhar

- Use `D:\ISIS_IA\AURORA` como projeto de codigo ativo.
- Leia primeiro `00_MASTER.md`.
- Consulte `PROJECT_STATUS.md`, `SESSION_LOG.md` e `docs/framework`.
- Preserve codigo existente e evite reescrever arquivos completos.
- Nao declare teste executado sem executar.

## Pontos criticos

- HUD web usado pelo usuario: `D:\ISIS_IA\AURORA\aurora\ui\hud_web.py`.
- Link web da IA: `http://127.0.0.1:8765/`.
- Porta `8787` e API, nao e a interface de conversa.
- Voz ativa/feminina: `dii_pt-BR`.
- Caminho da voz: `D:\ISIS_IA\ISIS\voice\piper\voices\OpenVoiceOS-pipertts_pt-BR_dii\dii_pt-BR.onnx`.
- Evite alterar `D:\ISIS_IA\ISIS\brain\cerebro_vivo` salvo quando a tarefa pedir cofre/Obsidian.

## Padrao de entrega

- Informe arquivo alterado, comando/link de teste e validacao real.
- Se houver bloqueio, registre causa tecnica exata.
- Se uma decisao arquitetural for tomada, registre em `docs/framework/DECISION_LOG.md`.
- Se corrigir erro operacional, registre em `docs/framework/BUGS_AND_SOLUTIONS.md`.

