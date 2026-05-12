# OpenMemoryRouter

**Self-hosted LLM routing platform** — OpenRouter alternative with semantic cache, EBM scoring, forecasting, diffusion planning, memory, and provider failover.

## Current Status: Phase 2 Complete

- OpenAI-compatible `/v1/chat/completions` (streaming + tools)
- 3-layer caching (exact + semantic + provider-native)
- EBM (Explainable Boosting Machine) forecasting & scoring
- Intelligent multi-strategy routing
- **Phase 2**: Postgres + Memory System + Feedback loop + Observability
- Basic dashboard at `/dashboard` (Phase 3)

## Quick Start

```bash
git clone https://github.com/mturac/openmemory-router.git
cd openmemory-router
cp .env.example .env
# Add your OPENROUTER_API_KEY
docker-compose up --build
```

API: http://localhost:8000  |  Dashboard: http://localhost:8000/dashboard (or open web/index.html)

## Phase Roadmap
- **Phase 1** (done): Core routing + cache + EBM
- **Phase 2** (done): Postgres + Memory + Feedback
- **Phase 3** (in progress): Full Next.js Dashboard + advanced observability
- **Phase 4**: Production hardening, local models, advanced diffusion planner

Built with ❤️ for people who want control over their LLM routing.