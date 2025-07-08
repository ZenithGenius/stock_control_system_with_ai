from typing import Any, Optional
import aioredis
import json
import hashlib
from config import REDIS_HOST, REDIS_PORT, REDIS_TTL

class CacheManager:
    def __init__(self):
        self.redis = None
        self.ttl = REDIS_TTL

    async def connect(self):
        if not self.redis:
            self.redis = aioredis.from_url(
                f'redis://{REDIS_HOST}:{REDIS_PORT}',
                decode_responses=True
            )

    async def disconnect(self):
        if self.redis:
            await self.redis.close()
            self.redis = None

    def generate_key(self, prefix: str, *args) -> str:
        """Generate a cache key from multiple arguments"""
        key_str = ":".join(str(arg) for arg in args)
        hash_obj = hashlib.md5(key_str.encode())
        return f"{prefix}:{hash_obj.hexdigest()}"

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            await self.connect()  # Ensure connection
            value = await self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Error getting from cache: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        try:
            await self.connect()  # Ensure connection
            ttl = ttl or self.ttl
            value_str = json.dumps(value)
            await self.redis.setex(key, ttl, value_str)
            return True
        except Exception as e:
            print(f"Error setting cache: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            await self.connect()  # Ensure connection
            return bool(await self.redis.delete(key))
        except Exception as e:
            print(f"Error deleting from cache: {e}")
            return False

    async def clear_all(self) -> bool:
        """Clear all cache"""
        try:
            await self.connect()  # Ensure connection
            await self.redis.flushall()
            return True
        except Exception as e:
            print(f"Error clearing cache: {e}")
            return False 