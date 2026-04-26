"""Simple in-memory TTL cache for lightweight memoization."""

import time
from functools import wraps
from typing import Any, Callable, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


class TTLCache:
    """Thread-safe (for CPython GIL) in-memory TTL cache."""

    def __init__(self, default_ttl: float = 60.0):
        self.default_ttl = default_ttl
        self._store: dict[str, tuple[Any, float]] = {}

    def get(self, key: str) -> Any | None:
        if key not in self._store:
            return None
        value, expires_at = self._store[key]
        if time.time() > expires_at:
            del self._store[key]
            return None
        return value

    def set(self, key: str, value: Any, ttl: float | None = None) -> None:
        expires_at = time.time() + (ttl or self.default_ttl)
        self._store[key] = (value, expires_at)

    def clear(self) -> None:
        self._store.clear()


def ttl_cache(ttl: float = 60.0) -> Callable[[F], F]:
    """Decorator that caches function results with TTL."""
    cache = TTLCache(default_ttl=ttl)

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            key = f"{func.__name__}:{hash(args + tuple(sorted(kwargs.items())))}"
            cached = cache.get(key)
            if cached is not None:
                return cached
            result = func(*args, **kwargs)
            cache.set(key, result, ttl=ttl)
            return result

        wrapper._cache = cache  # type: ignore[attr-defined]
        return wrapper  # type: ignore[return-value]

    return decorator

