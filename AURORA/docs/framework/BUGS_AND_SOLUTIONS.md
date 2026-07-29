# Bugs e solucoes

## Edicao inicial no projeto errado

- Problema: a interface foi alterada primeiro em `D:\ISIS_IA\ISIS\brain\cerebro_vivo\gui.py`, mas o usuario acessa o HUD web de `D:\ISIS_IA\AURORA`.
- Causa: havia mais de uma interface no workspace.
- Solucao: registrar `aurora/ui/hud_web.py` como HUD web ativo em `00_MASTER.md` e `AGENTS.md`.

## Voz Piper antiga nao encontrada

- Problema: HUD mostrava `piper voice not found` para `pt_BR-faber-medium`.
- Causa: `data/config.json` apontava para caminho inexistente.
- Solucao: configurar `piper_voice_path` para `D:\ISIS_IA\ISIS\voice\piper\voices\OpenVoiceOS-pipertts_pt-BR_dii\dii_pt-BR.onnx`.

## Link web incorreto ou servidor parado

- Problema: navegador mostrou conexao recusada em porta local.
- Causa: porta/servico incorreto ou HUD nao estava iniciado.
- Solucao: iniciar `python -m aurora.cli ui-hud-web --host 127.0.0.1 --port 8765` em `D:\ISIS_IA\AURORA`.

## Interface antiga por cache/processo antigo

- Problema: usuario ainda via HUD antigo.
- Causa: processo antigo na porta `8765` e cache do navegador.
- Solucao: reiniciar o servidor HUD e adicionar `Cache-Control: no-store` na resposta HTML.

## Botoes e navegacao sem acao real

- Problema: `MIC`, `ANEXO`, `PARAR` e menu lateral tinham comportamento incompleto ou apenas texto de status.
- Causa: HUD web inicial tinha HTML estatico e handlers minimos.
- Solucao: conectar menu a paineis, `MIC` ao ditado do navegador, `ANEXO` ao seletor local e `PARAR` ao cancelamento de voz/ditado/resposta pendente.

## Voz local robotica

- Problema: Piper `dii_pt-BR` funcionava, mas soava robotico no navegador.
- Causa: Piper local e leve, mas nao e neural/natural.
- Solucao: priorizar `speechSynthesis` com voz `pt-BR` do Chrome/Windows e manter Piper como fallback offline.

## TTS lendo Markdown literal

- Problema: respostas com Markdown eram enviadas diretamente ao TTS, fazendo a voz ler simbolos e formatacao.
- Causa: nao havia camada separada de preparacao de texto para fala.
- Solucao: criar `aurora.voice.text.prepare_text_for_speech` e aplicar antes de `speechSynthesis`, Piper e TTS mock.

## Microfone nao enviava comando automaticamente

- Problema: ditado pelo navegador preenchia o campo, mas exigia clique manual em `ENVIAR`.
- Causa: `recognition.onresult` apenas atualizava o input ao receber transcricao final.
- Solucao: chamar `sendPrompt()` automaticamente apos resultado final e bloquear envio duplicado com `sending`.

## Prompt de codigo caindo em mock

- Problema: perguntas como "voce consegue criar codigos" podiam cair em rota errada ou mock.
- Causa: roteamento nao cobria plural/acento de `codigo` e bloqueava modelos reais quando VRAM estava baixa.
- Solucao: detectar `codigo/codigo(s)` com regex acentuada e permitir uso via RAM quando ha RAM suficiente.

## Backlog de embeddings aparecia no chat

- Problema: a conversa inicial exibia `Embeddings de projetos: 25 indexadas, 83169 pendentes`.
- Causa: mensagem operacional de diagnostico foi colocada como bolha do chat.
- Solucao: trocar a bolha por texto humano curto e manter os numeros tecnicos nos paineis de memoria/status.

## HUD parecia travar apos enviar pergunta

- Problema: a tela aguardava a resposta completa antes de atualizar o resultado final.
- Causa: `/api/chat` executava geracao do modelo e sintese de voz no mesmo handler HTTP.
- Solucao: criar `ChatJobManager`, polling por `/api/chat-status`, cancelamento por `/api/chat-cancel` e persistencia em `hud_conversations.sqlite`.

## Footer sumia apos resposta longa

- Problema: apos resposta sobre codigo, nao aparecia opcao de falar nem digitar novamente.
- Causa: `.app` usava `min-height:100vh` com `overflow:hidden`; respostas longas empurravam o footer para fora do viewport.
- Solucao: fixar o HUD em `height:100vh`, usar linha central `minmax(0,1fr)`, manter `.workspace` rolavel e devolver foco ao input ao concluir/cancelar/erro.

## Motor natural nao validado localmente

- Problema: o pedido exige Kokoro/Chatterbox, mas nao havia modelo pt-BR instalado e validado.
- Causa: qualidade/licenca/pronuncia nao podem ser inferidas sem sintese real local.
- Solucao: implementar adaptadores compativeis via CLI/manifesto local; Piper fica como fallback enquanto Kokoro/Chatterbox nao forem configurados.

## Conversa sem rolagem propria

- Problema: a tela de mensagens nao exibia barra de rolagem clara para ver mensagens antigas/ultimas.
- Causa: a rolagem estava no container `workspace`, enquanto `#messages` nao tinha altura flex nem `overflow-y`.
- Solucao: tornar `#conversa` um container flex, aplicar `overflow-y:auto` em `#messages` e rolar automaticamente para o final ao adicionar/carregar mensagens.

## HUD puxava voz Microsoft Maria

- Problema: a voz da resposta ainda era a voz do Windows/Chrome.
- Causa: o HUD priorizava `speechSynthesis` e selecionava `Microsoft Maria - Portuguese (Brazil)`.
- Solucao: remover TTS do navegador para respostas e testes; tocar somente o audio local gerado pelo Piper.

## Audio local gerado mas sem som

- Problema: o HUD indicava `Audio gerado; autoplay bloqueado pelo navegador` e nao saia voz automaticamente.
- Causa: Chrome pode bloquear `Audio.play()` apos retorno assincrono do servidor.
- Solucao: anexar um player `audio controls` em cada resposta/teste com WAV local para o usuario tocar manualmente quando autoplay for bloqueado.

## Pesquisa sem fonte parseavel no DuckDuckGo HTML

- Problema: a pesquisa real retornou HTML, mas sem resultados extraidos pelo parser DuckDuckGo neste ambiente.
- Causa: markup/resposta publica do buscador variou.
- Solucao: adicionar fallback `bing_html` e decodificar URLs finais de redirecionamento.

## Pagina externa retornou conteudo compactado no trecho

- Problema: uma fonte retornou bytes gzip no excerto.
- Causa: servidor ignorou ou variou `Accept-Encoding`.
- Solucao: forcar `Accept-Encoding: identity`, descompactar gzip quando indicado e remover caracteres de controle.
