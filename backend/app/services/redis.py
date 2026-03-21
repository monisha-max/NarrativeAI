import orjson
import structlog

from app.config import settings

logger = structlog.get_logger()


class RedisService:
    """Redis service for session memory, delta state, and caching. Falls back to in-memory dict."""

    def __init__(self):
        self.client = None
        self.available = False
        self._fallback_cache: dict[str, str] = {}

        if settings.redis_url:
            try:
                import redis.asyncio as redis
                self.client = redis.from_url(settings.redis_url, decode_responses=True)
                self.available = True
            except Exception as e:
                logger.warning("redis.init.failed", error=str(e))

    async def _check_connection(self):
        """Verify Redis is actually reachable."""
        if self.client and not self.available:
            return
        if self.client:
            try:
                await self.client.ping()
                self.available = True
            except Exception:
                self.available = False

    async def get_session_state(self, user_id: str, dossier_id: str) -> dict | None:
        key = f"session:{user_id}:{dossier_id}"
        if self.available:
            try:
                data = await self.client.get(key)
                if data:
                    return orjson.loads(data)
            except Exception:
                pass
        # Fallback
        data = self._fallback_cache.get(key)
        if data:
            return orjson.loads(data)
        return None

    async def set_session_state(self, user_id: str, dossier_id: str, state: dict):
        key = f"session:{user_id}:{dossier_id}"
        value = orjson.dumps(state).decode()
        if self.available:
            try:
                await self.client.set(key, value, ex=60 * 60 * 24 * 30)
                return
            except Exception:
                pass
        self._fallback_cache[key] = value

    async def cache_dossier(self, slug: str, data: dict, ttl: int = 3600):
        key = f"dossier_cache:{slug}"
        value = orjson.dumps(data).decode()
        if self.available:
            try:
                await self.client.set(key, value, ex=ttl)
                return
            except Exception:
                pass
        self._fallback_cache[key] = value

    async def get_cached_dossier(self, slug: str) -> dict | None:
        key = f"dossier_cache:{slug}"
        if self.available:
            try:
                data = await self.client.get(key)
                if data:
                    return orjson.loads(data)
            except Exception:
                pass
        data = self._fallback_cache.get(key)
        if data:
            return orjson.loads(data)
        return None

    async def close(self):
        if self.client:
            try:
                await self.client.close()
            except Exception:
                pass


redis_service = RedisService()
