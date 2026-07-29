# Arquitetura de Voz ISIS

## Estado implementado

- Gerenciador: `aurora.voice.voice_manager.VoiceManager`.
- Roteador TTS: `aurora.voice.voice_router.VoiceRouter`.
- Fallback: Kokoro compativel via CLI/manifesto local -> Chatterbox compativel via CLI/manifesto local -> Piper local -> texto/mock quando indisponivel.
- TTS ativo validado: Piper `dii_pt-BR`.
- Normalizacao PT-BR: `aurora.voice.text_normalizer.PortugueseSpeechNormalizer`.
- Cache: `aurora.voice.tts.piper_engine.AudioCache`.
- Fila/interrupcao: `SpeechQueue`, `InterruptionManager`, `VoiceActivityDetector`.
- STT local preparado: `WhisperCppSTTEngine`, dependente de binario/modelo configurado.

## Decisao

Kokoro e Chatterbox nao foram rejeitados. Eles entram como adaptadores compativeis: quando `data/config.json` apontar para um comando local ou `tts_manifest.json` valido, passam a ser usados pelo roteador. Piper segue como fallback offline funcional enquanto nao houver instalacao local configurada.
