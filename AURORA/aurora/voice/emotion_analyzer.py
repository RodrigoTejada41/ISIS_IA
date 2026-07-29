from __future__ import annotations


class EmotionAnalyzer:
    def classify(self, text: str) -> str:
        value = str(text or "").lower()
        if any(word in value for word in ("erro", "falha", "caiu", "problema")):
            return "focused"
        if any(word in value for word in ("concluido", "sucesso", "pronto", "excelente")):
            return "happy"
        if any(word in value for word in ("atenção", "atencao", "perigo", "bloqueado")):
            return "warning"
        if any(word in value for word in ("bom dia", "boa tarde", "ola", "olá")):
            return "friendly"
        return "neutral"

