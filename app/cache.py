import hashlib
import json
import redis.asyncio as redis
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

class UltraCache:
    def __init__(self):
        self.redis = redis.from_url("redis://redis:6379/0")
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = faiss.IndexFlatIP(384)
        self.id_to_response = {}

    async def get_exact(self, prompt: str, model: str):
        key = f"exact:{model}:{hashlib.sha256(prompt.encode()).hexdigest()}"
        data = await self.redis.get(key)
        return json.loads(data) if data else None

    async def set_exact(self, prompt: str, model: str, response: dict, ttl: int = 7200):
        key = f"exact:{model}:{hashlib.sha256(prompt.encode()).hexdigest()}"
        await self.redis.setex(key, ttl, json.dumps(response))

    async def get_semantic(self, prompt: str, threshold: float = 0.93):
        vec = self.embedder.encode([prompt])[0].astype('float32')
        D, I = self.index.search(np.array([vec]), 1)
        if len(D[0]) > 0 and D[0][0] > threshold and I[0][0] in self.id_to_response:
            return self.id_to_response[I[0][0]]
        return None

    async def set_semantic(self, prompt: str, response: dict):
        vec = self.embedder.encode([prompt])[0].astype('float32')
        idx = len(self.id_to_response)
        self.index.add(np.array([vec]))
        self.id_to_response[idx] = response