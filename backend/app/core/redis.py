import logging

import redis

from app.core.settings import settings

logger = logging.getLogger("app.core.redis")


class CacheManager:
    def __init__(self):
        self.client = None
        self._local_cache = {}
        try:
            if getattr(settings, "REDIS_URL", None):
                self.client = redis.Redis.from_url(
                    settings.REDIS_URL,
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
                    retry=None,
                    decode_responses=True,
                )
            # Ping check
            self.client.ping()
            logger.info("Successfully connected to Redis cache provider.")
        except Exception as e:
            logger.warning(
                f"Redis is unavailable: {e}. Cache manager falling back to local simulation."
            )
            self.client = None

    def get(self, key: str) -> str | None:
        if self.client:
            try:
                return self.client.get(key)
            except Exception:
                pass
        return self._local_cache.get(key)

    def set(self, key: str, value: str, expire_seconds: int = 3600) -> bool:
        if self.client:
            try:
                self.client.set(key, value, ex=expire_seconds)
                return True
            except Exception:
                pass
        self._local_cache[key] = value
        return True

    def delete(self, key: str) -> bool:
        if self.client:
            try:
                self.client.delete(key)
                return True
            except Exception:
                pass
        if key in self._local_cache:
            del self._local_cache[key]
        return True

    def ping(self) -> bool:
        if self.client:
            try:
                return bool(self.client.ping())
            except Exception:
                return False
        return True


cache_manager = CacheManager()
