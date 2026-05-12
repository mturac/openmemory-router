import numpy as np
from datetime import datetime
import structlog

logger = structlog.get_logger()

class EBMLatencyCostForecaster:
    def predict(self, prompt: str, messages: list, model: str) -> dict:
        prompt_len = len(prompt)
        keyword_score = sum(1 for w in ["analiz", "a\u00e7\u0131kla", "reason", "step by step", "complex", "kar\u015f\u0131la\u015ft\u0131r"] if w in prompt.lower())
        model_idx = 1 if any(x in model.lower() for x in ["gpt-4", "claude"]) else 0
        hour = datetime.utcnow().hour
        is_complex = 1 if keyword_score > 2 else 0

        predicted_latency = 280 + (prompt_len / 8) + (keyword_score * 45)
        predicted_cost = 0.001 + (prompt_len / 18000)

        return {
            "predicted_latency_ms": predicted_latency,
            "predicted_cost": predicted_cost,
            "failure_prob": 0.03,
            "quality_score": 0.92 if model_idx == 1 else 0.8
        }

    def score_route(self, forecast: dict, cache_hit: bool = False) -> float:
        energy = (
            0.35 * forecast["predicted_cost"] +
            0.25 * (forecast["predicted_latency_ms"] / 1000) +
            0.2 * forecast.get("failure_prob", 0.05) -
            (0.2 if cache_hit else 0)
        )
        return max(0.01, energy)