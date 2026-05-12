import litellm
from .forecaster import EBMLatencyCostForecaster
from .cache import UltraCache
from .memory import memory
import structlog

logger = structlog.get_logger()

class SmartRouter:
    def __init__(self):
        self.cache = UltraCache()
        self.forecaster = EBMLatencyCostForecaster()

    async def route(self, body: dict, headers: dict):
        messages = body.get("messages", [])
        model = body.get("model", "openai/gpt-4o-mini")
        prompt = " ".join([m.get("content", "") for m in messages])
        stream = body.get("stream", False)

        # Security: basic length check
        if len(prompt) > 50000:
            raise ValueError("Prompt too long")

        # 1. Exact cache
        cached = await self.cache.get_exact(prompt, model)
        if cached and not stream:
            logger.info("exact_cache_hit")
            return cached

        # 2. Semantic cache
        semantic_hit = await self.cache.get_semantic(prompt)
        if semantic_hit and not stream:
            logger.info("semantic_cache_hit")
            return semantic_hit

        # 3. Forecast
        forecast = self.forecaster.predict(prompt, messages, model)

        # 4. Intelligent routing with EBM scoring
        energy_cheap = self.forecaster.score_route(forecast, cache_hit=False)
        energy_quality = energy_cheap * 0.7 + 0.3  # favor quality slightly

        if energy_cheap < 0.6:
            target_model = "openai/gpt-4o-mini"
        elif energy_quality < 0.9:
            target_model = model
        else:
            target_model = "openai/gpt-4o"  # fallback to stronger

        # 5. Call via LiteLLM (supports OpenRouter + all major providers)
        extra_headers = {
            "HTTP-Referer": headers.get("http-referer", ""),
            "X-OpenRouter-Title": headers.get("x-openrouter-title", "OpenMemoryRouter")
        }

        response = await litellm.acompletion(
            model=target_model,
            messages=messages,
            stream=stream,
            extra_headers=extra_headers,
            **{k: v for k, v in body.items() if k not in ["messages", "model", "stream"]}
        )

        if stream:
            return response

        resp_dict = response.model_dump()

        # 6. Remember + Cache
        ttl = 10800 if forecast["predicted_cost"] < 0.003 else 3600
        await self.cache.set_exact(prompt, model, resp_dict, ttl)
        await self.cache.set_semantic(prompt, resp_dict)
        await memory.remember_route(
            hashlib.sha256(prompt.encode()).hexdigest(),
            target_model.split("/")[0] if "/" in target_model else target_model,
            target_model,
            self.forecaster.score_route(forecast)
        )

        logger.info(f"routed_to={target_model} energy={self.forecaster.score_route(forecast):.3f}")
        return resp_dict