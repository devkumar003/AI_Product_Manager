import logging
import time
import redis.asyncio as redis

from app.core.settings import settings

logger = logging.getLogger("app.core.redis")

class CacheManager:
    def __init__(self):
        self.client = None
        self._local_cache = {}
        self._last_connect_attempt = 0
        self._connect_cooldown = 10  # Seconds before retrying connection
        self._connect()

    def _connect(self):
        now = time.time()
        if now - self._last_connect_attempt < self._connect_cooldown:
            return
            
        self._last_connect_attempt = now
        try:
            redis_url = getattr(settings, "REDIS_URL", None)
            if redis_url and any(redis_url.startswith(scheme) for scheme in ("redis://", "rediss://", "unix://")):
                self.client = redis.Redis.from_url(
                    redis_url,
                    socket_connect_timeout=0.5,
                    socket_timeout=0.5,
                    decode_responses=True,
                )
            else:
                self.client = redis.Redis(
                    host=settings.REDIS_HOST,
                    port=settings.REDIS_PORT,
                    password=getattr(settings, "REDIS_PASSWORD", None),
                    socket_connect_timeout=0.25,
                    socket_timeout=0.25,
                    retry_on_timeout=False,
                    decode_responses=True,
                )
            logger.info("Successfully configured async Redis cache provider.")
        except Exception as e:
            logger.warning(
                f"Redis configuration failed: {e}. Cache manager falling back to local simulation."
            )
            self.client = None

    async def get(self, key: str) -> str | None:
        if not self.client:
            self._connect()
            
        if self.client:
            try:
                return await self.client.get(key)
            except Exception:
                self.client = None
                pass
                
        # Local cache fallback with expiration check
        if key in self._local_cache:
            value, expires_at = self._local_cache[key]
            if expires_at and time.time() > expires_at:
                del self._local_cache[key]
                return None
            return value
        return None

    async def set(self, key: str, value: str, expire_seconds: int = 3600) -> bool:
        if not self.client:
            self._connect()
            
        if self.client:
            try:
                await self.client.set(key, value, ex=expire_seconds)
                return True
            except Exception:
                self.client = None
                pass
                
        expires_at = time.time() + expire_seconds if expire_seconds else None
        self._local_cache[key] = (value, expires_at)
        
        # Cleanup expired items occasionally to prevent memory leak
        if len(self._local_cache) % 100 == 0:
            self._cleanup_local()
            
        return True

    async def delete(self, key: str) -> bool:
        if not self.client:
            self._connect()
            
        if self.client:
            try:
                await self.client.delete(key)
                return True
            except Exception:
                self.client = None
                pass
                
        if key in self._local_cache:
            del self._local_cache[key]
        return True

    async def ping(self) -> bool:
        if not self.client:
            self._connect()
            
        if self.client:
            try:
                return await self.client.ping()
            except Exception:
                self.client = None
                return False
        return True

    def _cleanup_local(self):
        now = time.time()
        expired = [k for k, v in self._local_cache.items() if v[1] and now > v[1]]
        for k in expired:
            del self._local_cache[k]

cache_manager = CacheManager()
