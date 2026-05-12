import asyncio
import time
from app.router import SmartRouter

async def run_benchmark():
    router = SmartRouter()
    total = 500
    hits = 0
    latencies = []
    print("Running benchmark (500 requests)...")
    start = time.time()
    for i in range(total):
        prompt = f"Test prompt {i} - {'complex analysis and reasoning' if i % 5 == 0 else 'simple greeting'}"
        body = {
            "model": "openai/gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}]
        }
        t0 = time.time()
        await router.route(body, {})
        latency = (time.time() - t0) * 1000
        latencies.append(latency)
        if latency < 100:
            hits += 1
    total_time = time.time() - start
    avg = sum(latencies) / total
    print(f"Benchmark complete: {hits/total*100:.1f}% cache hits, avg latency {avg:.1f}ms, total time {total_time:.1f}s")

if __name__ == "__main__":
    asyncio.run(run_benchmark())