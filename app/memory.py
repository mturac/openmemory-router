import structlog
from .db import db

logger = structlog.get_logger()

class MemorySystem:
    def __init__(self):
        self.short_term = {}

    async def remember_route(self, prompt_hash: str, provider: str, model: str, energy: float):
        await db.execute("""
            INSERT INTO route_memory (prompt_hash, best_provider, best_model, energy_score, success_count, last_used)
            VALUES ($1, $2, $3, $4, 1, NOW())
            ON CONFLICT (prompt_hash) DO UPDATE
            SET best_provider = $2, best_model = $3, energy_score = $4,
                success_count = route_memory.success_count + 1, last_used = NOW()
        """, prompt_hash, provider, model, energy)
        logger.info(f"Remembered successful route for {prompt_hash[:12]}...")

    async def get_best_route(self, prompt_hash: str):
        row = await db.fetchrow("SELECT best_provider, best_model, energy_score FROM route_memory WHERE prompt_hash = $1 ORDER BY last_used DESC LIMIT 1", prompt_hash)
        return dict(row) if row else None

    async def record_feedback(self, request_id: str, rating: int, accepted: bool, notes: str = ""):
        await db.execute("""
            INSERT INTO feedback (request_id, rating, accepted, notes, created_at)
            VALUES ($1, $2, $3, $4, NOW())
        """, request_id, rating, accepted, notes)
        logger.info(f"Feedback recorded: request={request_id}, rating={rating}, accepted={accepted}")

memory = MemorySystem()