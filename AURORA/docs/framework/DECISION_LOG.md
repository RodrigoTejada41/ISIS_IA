# Decision Log

## 2026-07-28 - Projeto ativo da interface

- Decisao: o HUD web usado pelo usuario pertence ao projeto `D:\ISIS_IA\AURORA`.
- Motivo: o link local `http://127.0.0.1:8765/` e servido por `aurora.cli ui-hud-web`.
- Consequencia: mudancas de interface web devem ser feitas em `aurora/ui/hud_web.py`.

## 2026-07-28 - Voz feminina padrao

- Decisao: a voz padrao aceita para ISIS e OpenVoiceOS Piper `dii_pt-BR`.
- Motivo: usuario rejeitou a voz masculina/anterior e indicou `isis_openvoiceos_ptbr_dii.wav` como feminina.
- Consequencia: `data/config.json` deve apontar para `OpenVoiceOS-pipertts_pt-BR_dii\dii_pt-BR.onnx`.

## 2026-07-28 - Separacao de portas

- Decisao: porta `8765` e a interface web; porta `8787` e API de conhecimento.
- Motivo: usuario tentou acessar a IA no navegador e recebeu erro ao usar a porta errada/servico parado.
- Consequencia: sempre informar `http://127.0.0.1:8765/` como link de acesso a IA.

## 2026-07-28 - Framework local

- Decisao: aplicar `Development_Framework` como camada de governanca em `D:\ISIS_IA\AURORA`.
- Motivo: o projeto estava perdendo contexto e houve edicao inicial no local errado.
- Consequencia: novas sessoes devem iniciar por `00_MASTER.md` e `docs/framework`.

## 2026-07-28 - Voz e microfone no HUD web

- Decisao: usar APIs nativas do navegador para voz natural e ditado no HUD web.
- Motivo: Piper local e funcional, mas a voz e mais robotica; Chrome/Windows pode oferecer vozes `pt-BR` mais naturais sem instalar modelo pesado.
- Consequencia: `VOZ NATURAL` usa `speechSynthesis`; `MIC` usa `SpeechRecognition` quando disponivel e autorizado no navegador.

## 2026-07-29 - Voz local obrigatoria no HUD

- Decisao: respostas e teste de voz do HUD web usam somente audio local gerado por Piper.
- Motivo: o usuario rejeitou a voz `Microsoft Maria` do Windows/Chrome.
- Consequencia: `speechSynthesis` deixa de ser usado no HUD; `MIC` permanece usando `SpeechRecognition` apenas para ditado.

## 2026-07-28 - Texto separado para fala

- Decisao: manter a resposta exibida intacta e gerar uma versao limpa apenas para TTS.
- Motivo: Markdown, listas, links e blocos de codigo prejudicam a fala quando enviados como texto bruto.
- Consequencia: todos os providers TTS devem receber texto preparado por `prepare_text_for_speech`.

## 2026-07-28 - Roteamento real antes de mock

- Decisao: VRAM baixa nao deve forcar mock se houver RAM suficiente para Ollama.
- Motivo: o usuario espera resposta real do modelo local, nao eco `[mock:*]`.
- Consequencia: o roteador pode escolher modelo real com `VRAM insufficient; using RAM`.

## 2026-07-28 - HUD web assincrono e historico local

- Decisao: `/api/chat` deve iniciar um job e retornar imediatamente, com polling por `/api/chat-status`.
- Motivo: gerar texto, TTS e I/O dentro do request longo deixava a interface sem feedback e com aparencia de travamento.
- Consequencia: conversas sao persistidas em SQLite e a UI usa estados visuais de analise, geracao, voz, conclusao e erro.

## 2026-07-28 - Footer fixo no HUD web

- Decisao: no desktop, o HUD web ocupa `height:100vh` e apenas a area central de conversa rola.
- Motivo: respostas longas nao podem ocultar a barra de digitar, `MIC`, `ENVIAR` e `PARAR`.
- Consequencia: o footer permanece visivel e o input recebe foco apos conclusao, cancelamento ou erro do job.

## 2026-07-28 - Arquitetura modular de voz local

- Decisao: criar `VoiceManager` e `VoiceRouter` com Piper como fallback validado e Kokoro/Chatterbox como motores opcionais indisponiveis ate validacao local.
- Motivo: nao ha modelo Kokoro/Chatterbox pt-BR validado no workspace; definir qualquer um como padrao seria afirmacao nao comprovada.
- Consequencia: a ISIS ganha fallback, cache, normalizacao, benchmark e diagnostico sem perder a voz Piper funcional.

## 2026-07-28 - Compatibilidade Kokoro/Chatterbox

- Decisao: Kokoro e Chatterbox nao sao rejeitados; sao adaptadores compativeis via comando local ou `tts_manifest.json`.
- Motivo: o usuario quer manter esses motores elegiveis, mas ainda sem inventar pacote/modelo pt-BR nao validado.
- Consequencia: quando houver instalacao local configurada, o roteador usa Kokoro/Chatterbox antes do fallback Piper.

## 2026-07-28 - Internet controlada e Central de Regras

- Decisao: implementar Internet em modo controlado com `PermissionEngine` central, SSRF obrigatorio e pesquisa por HTTP simples.
- Motivo: a ISIS precisa pesquisar sem API paga obrigatoria e sem transformar acesso online em permissao irrestrita.
- Consequencia: pesquisas publicas passam por permissao, dominio, sanitizacao, cache e historico; downloads executaveis seguem bloqueados.
