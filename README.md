# OpenMemoryRouter

**Self-hosted LLM routing platform** - OpenRouter alternative with semantic cache, EBM scoring, forecasting, diffusion planning, memory, and provider failover.

## Features
- OpenAI-compatible API (`/v1/chat/completions`)
- Multi-provider support via LiteLLM (OpenAI, Anthropic, Groq, Gemini, etc.)
- 3-layer caching (exact + semantic + provider-native)
- EBM (Explainable Boosting Machine) for route scoring
- Forecasting for cost, latency, quality
- Intelligent routing with multiple strategies
- Memory system for learning from usage
- Feedback loop for continuous improvement
- Streaming support
- Tool calling passthrough

## Quick Start

```bash
git clone https://github.com/mturac/openmemory-router.git
cd openmemory-router
cp .env.example .env
# Edit .env with your OPENROUTER_API_KEY
 docker-compose up --build
```

API will be available at http://localhost:8000

Test:
```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "openai/gpt-4o-mini", "messages": [{"role": "user", "content": "Hello"}]}'
```

## Architecture
- FastAPI backend
- LiteLLM for provider abstraction
- Redis for hot cache and short-term memory
- FAISS for semantic cache
- EBM for explainable route scoring

This is a production-ready foundation. Full monorepo with Next.js dashboard, Prisma, advanced diffusion planner, and more coming in next phases.