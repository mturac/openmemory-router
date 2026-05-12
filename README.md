# OpenMemoryRouter

**Self-hosted LLM routing platform** — OpenRouter alternative with semantic cache, EBM scoring, forecasting, diffusion planning, memory, and provider failover.

## Status: Phase 4 Complete (Production Ready MVP)

- Full OpenAI-compatible `/v1/chat/completions` + streaming + tools
- 3-layer caching (exact + semantic + provider-native)
- EBM forecasting + scoring with explainability
- Intelligent routing with energy-based decisions
- **Phase 2**: Postgres + Memory System + Feedback loop
- **Phase 3**: Dashboard (web/index.html)
- **Phase 4**: Security, local providers, production polish

## Quick Start

```bash
git clone https://github.com/mturac/openmemory-router.git
cd openmemory-router
cp .env.example .env
docker-compose up --build
```

**API**: http://localhost:8000  
**Dashboard**: Open `web/index.html` in browser

## Key Features
- Learns from usage (memory + feedback)
- Predicts cost/latency/quality before routing
- Explainable decisions ("Why this provider?")
- Multi-tenant ready foundation
- Works with any OpenAI-compatible provider (local or cloud)

This is a serious, production-grade foundation. Not a toy.