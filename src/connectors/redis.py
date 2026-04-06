import asyncio
import json
import logging
from typing import Any

from redis import asyncio as aioredis
from redis.backoff import ExponentialBackoff
from redis.exceptions import ConnectionError, TimeoutError
from redis.retry import Retry

from config import settings

logger = logging.getLogger(__name__)


class RedisManager:
    """
    Обёртка над redis.asyncio.Redis с:
    - пулом соединений
    - retry/backoff на уровне соединения
    - логированием
    """

    def __init__(
        self,
        url: str,
        *,
        decode_responses: bool = False,
        socket_timeout: float | None = 5.0,
        socket_connect_timeout: float | None = 5.0,
        max_connections: int = 50,
        # настройки для retry redis-py, задержка = min(retry_backoff_max, retry_backoff_base * 2**failures)
        retry_count: int = 5,
        retry_backoff_base: float = 0.5,
        retry_backoff_max: float = 5.0,
        health_check_interval: int = 30,
    ) -> None:
        self._url = url
        self._decode_responses = decode_responses
        self._socket_timeout = socket_timeout
        self._socket_connect_timeout = socket_connect_timeout
        self._max_connections = max_connections
        self._health_check_interval = health_check_interval

        self._retry_retries = retry_count
        self._retry_backoff_base = retry_backoff_base
        self._retry_backoff_cap = retry_backoff_max

        self._client: aioredis.Redis | None = None
        self._lock = asyncio.Lock()

    @property
    def client(self) -> aioredis.Redis:
        if self._client is None:
            raise RuntimeError("RedisManager is not connected. Call await connect() first.")
        return self._client

    async def connect(self) -> None:
        """
        Создаёт async‑клиент и пул соединений.

        Вызывать один раз при старте приложения.
        """
        async with self._lock:
            if self._client is not None:
                return

            backoff = ExponentialBackoff(
                base=self._retry_backoff_base,
                cap=self._retry_backoff_cap,
            )
            retry = Retry(
                backoff=backoff,
                retries=self._retry_retries,
            )

            logger.info("Connecting to Redis: url=%s", self._url)

            self._client = aioredis.from_url(
                self._url,
                decode_responses=self._decode_responses,
                socket_timeout=self._socket_timeout,
                socket_connect_timeout=self._socket_connect_timeout,
                max_connections=self._max_connections,
                retry=retry,
                retry_on_error=[ConnectionError, TimeoutError],
                health_check_interval=self._health_check_interval,
            )

            try:
                await self._client.ping()
            except Exception:
                logger.exception("Failed to connect to Redis on initial ping")
                await self.close()
                raise

            logger.info("Redis connection established")

    async def close(self) -> None:
        """
        Корректно закрывает соединения с Redis.

        Вызывать при остановке приложения.
        """
        async with self._lock:
            if self._client is not None:
                logger.info("Closing Redis connection")
                try:
                    await self._client.close()
                    if hasattr(self._client, "connection_pool"):
                        await self._client.connection_pool.disconnect()  # type: ignore[attr-defined]
                except Exception:
                    logger.exception("Error while closing Redis connection")
                finally:
                    self._client = None

    # ===== Базовые операции =====

    async def get(self, key: str) -> str | bytes | None:
        try:
            return await self.client.get(key)
        except (ConnectionError, TimeoutError):
            logger.exception("Redis GET failed: key=%s", key)
            raise

    async def set(
        self,
        key: str,
        value: str | bytes,
        *,
        ex: int | None = None,
        px: int | None = None,
        nx: bool | None = None,
        xx: bool | None = None,
    ) -> bool:
        try:
            res = await self.client.set(key, value, ex=ex, px=px, nx=nx, xx=xx)
            return bool(res)
        except (ConnectionError, TimeoutError):
            logger.exception("Redis SET failed: key=%s", key)
            raise

    async def delete(self, *keys: str) -> int:
        try:
            return int(await self.client.delete(*keys))
        except (ConnectionError, TimeoutError):
            logger.exception("Redis DEL failed: keys=%s", keys)
            raise

    async def exists(self, key: str) -> bool:
        try:
            return bool(await self.client.exists(key))
        except (ConnectionError, TimeoutError):
            logger.exception("Redis EXISTS failed: key=%s", key)
            raise

    # ===== JSON helper‑ы =====

    async def set_json(
        self,
        key: str,
        value: Any,
        *,
        ex: int | None = None,
    ) -> bool:
        payload = json.dumps(value, separators=(",", ":"))
        return await self.set(key, payload, ex=ex)

    async def get_json(self, key: str) -> Any | None:
        raw = await self.get(key)
        if raw is None:
            return None

        if isinstance(raw, bytes):
            raw = raw.decode("utf-8")

        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            logger.warning("Invalid JSON in Redis key=%s", key)
            return None

    # ===== Пример: simple lock (Lua + eval) =====

    async def acquire_lock(
        self,
        key: str,
        value: str,
        *,
        ttl: int = 30,
    ) -> bool:
        """
        Простейший распределённый lock: SET key value NX EX ttl.
        """
        try:
            return await self.set(key, value, ex=ttl, nx=True)
        except (ConnectionError, TimeoutError):
            logger.exception("Redis acquire_lock failed: key=%s", key)
            raise

    async def release_lock(self, key: str, value: str) -> None:
        """
        Безопасный unlock через Lua (проверка value).

        Для сложных кейсов см. Redlock/оф. рекомендации Redis.
        """
        lua = """
        if redis.call("GET", KEYS[1]) == ARGV[1] then
            return redis.call("DEL", KEYS[1])
        else
            return 0
        end
        """
        try:
            # numkeys=1, потом KEYS[1], потом ARGV[1]
            await self.client.eval(lua, 1, key, value)
        except (ConnectionError, TimeoutError):
            logger.exception("Redis release_lock failed: key=%s", key)
            raise


# Пример использования


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    manager = RedisManager("redis://localhost:6379/0")

    await manager.connect()

    await manager.set_json("user:1", {"id": 1, "name": "Alice"}, ex=60)
    data = await manager.get_json("user:1")
    print(data)

    await manager.close()


if __name__ == "__main__":
    asyncio.run(main())

redis_manager = RedisManager(url=settings.REDIS_URL)
