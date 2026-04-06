import asyncio
import functools
import hashlib
import json
from typing import Callable, Any

from fastapi.encoders import jsonable_encoder

from connectors import redis_manager


async def _cache_call(
    func: Callable[..., Any],
    args: tuple,
    kwargs: dict,
    key: str,
    exp: int | None = None,
):
    is_async = asyncio.iscoroutinefunction(func)
    try:
        data = await redis_manager.get_json(key)
    except Exception:
        return await func(*args, **kwargs) if is_async else func(*args, **kwargs)
    if data is None:
        data = await func(*args, **kwargs) if is_async else func(*args, **kwargs)
        encoded = jsonable_encoder(data)
        await redis_manager.set_json(key=key, value=encoded, ex=exp)
    return data


def cache(exp: int | None = None):
    def decorator(func):
        qualname = f"{func.__module__}.{func.__qualname__}"

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            key = _generate_key(qualname, args, kwargs)
            return await _cache_call(func, args, kwargs, key, exp)

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            key = _generate_key(qualname, args, kwargs)
            return asyncio.run(_cache_call(func, args, kwargs, key, exp))

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator


def _generate_key(func_name: str, args: tuple, kwargs: dict) -> str:
    payload = {
        "args": args,
        "kwargs": kwargs,
    }
    raw = json.dumps(payload, sort_keys=True, default=str)
    digest = hashlib.md5(raw.encode("utf-8")).hexdigest()
    return f"{func_name}:{digest}"
