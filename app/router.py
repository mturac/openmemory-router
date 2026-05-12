import litellm
from .forecaster import EBMLatencyCostForecaster
from .cache import UltraCache
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

        # 1. Check exact cache
        cached = await self.cache.get_exact(prompt, model)
        if cached and not stream:
            logger.info("exact_cache_hit")
            return cached

        # 2. Check semantic cache
        semantic_hit = await self.cache.get_semantic(prompt)
        if semantic_hit and not stream:
            logger.info("semantic_cache_hit")
            return semantic_hit

        # 3. Forecast
        forecast = self.forecaster.predict(prompt, messages, model)

        # 4. Simple routing logic (can be expanded with EBM scoring)
        if forecast["predicted_latency_ms"] < 500 and forecast["predicted_cost"] < 0.005:
            target_model = "openai/gpt-4o-mini"
        else:
            target_model = model

        # 5. Call provider via LiteLLM
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

        # 6. Cache the response
        ttl = 7200
        await self.cache.set_exact(prompt, model, resp_dict, ttl)
        await self.cache.set_semantic(prompt, resp_dict)

        logger.info(f"routed_to={target_model} latency_pred={forecast['predicted_latency_ms']:.0f}ms")
        return resp_dict