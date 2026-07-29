# Tarefas atuais

## Concluido

- Identificado que o HUD web correto fica em `D:\ISIS_IA\AURORA\aurora\ui\hud_web.py`.
- Corrigida configuracao de voz para `dii_pt-BR`.
- Baixada voz OpenVoiceOS Piper `OpenVoiceOS-pipertts_pt-BR_dii`.
- Gerado teste WAV em `D:\ISIS_IA\ISIS\data\temporary\isis_openvoiceos_ptbr_dii.wav`.
- Redesenhada interface web HUD no projeto AURORA.
- Reiniciado servidor HUD web em `http://127.0.0.1:8765/`.
- Validado HTML novo com `VOICE_DII=True`.
- Aplicado `Development_Framework` ao projeto AURORA.
- Botao `MIC` conectado ao ditado do navegador via Web Speech Recognition.
- Voz web natural priorizada via SpeechSynthesis do Chrome/Windows, com Piper como fallback.
- Navegacao lateral agora troca paineis funcionais.
- `ANEXO` abre seletor local e registra arquivos selecionados.
- `PARAR` cancela voz/ditado e interrompe resposta pendente no cliente.
- `/api/chat` agora usa jobs assincronos com polling.
- Conversas do HUD web sao salvas em SQLite.
- Barra lateral mostra projetos e conversas recentes.
- Botoes de copiar, tentar novamente e editar pergunta foram adicionados nas respostas.
- Criada arquitetura modular de voz local com fallback Piper, cache, normalizador PT-BR, fila e diagnostico.
- Kokoro/Chatterbox agora possuem adaptador compativel via comando local ou `tts_manifest.json`.

## Pendente

- Validacao visual final do usuario no navegador com `Ctrl+F5`.
- STT server-side real com `whisper.cpp` continua pendente; o microfone atual usa API do navegador.
- Validar qualidade/pronuncia Kokoro/Chatterbox com modelo pt-BR real antes de trocar o motor padrao.
- Medir RAM/VRAM do benchmark de voz com motor neural instalado.
- Envio real de anexos ao modelo continua pendente; selecao local ja funciona.
- Exportacao, arquivamento, favoritos e lixeira ainda estao preparados visualmente, mas exigem endpoints especificos.
- Continuar embeddings pendentes do indice grande de projetos.
