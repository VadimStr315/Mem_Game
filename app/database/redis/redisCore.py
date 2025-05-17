import redis.asyncio as aioredis
from decouple import config

class RedisClient:
    def __init__(self, host=config('REDIS_HOST', default='redis'), port=config('REDIS_PORT', default=6379)):
        self.host = host
        self.port = port
        self.redis = None

    async def connect(self):
        self.redis = await aioredis.from_url(f"redis://{self.host}:{self.port}")

    async def set(self, key: str, value: str, expire: int):
        await self.redis.set(key, value, ex=expire)

    async def get(self, key: str):
        return await self.redis.get(key)

    async def delete(self, key: str):
        await self.redis.delete(key)

    async def close(self):
        await self.redis.close()