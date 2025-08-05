#!/usr/bin/env python3
"""
Redis caching module with call replay functionality
"""

import redis
import uuid
from typing import Union, Callable, Optional, Any
from functools import wraps


def count_calls(method: Callable) -> Callable:
    """Decorator to count method calls"""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        key = method.__qualname__
        self._redis.incr(key)
        return method(self, *args, **kwargs)
    return wrapper


def call_history(method: Callable) -> Callable:
    """Decorator to store call history in Redis lists"""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        input_key = f"{method.__qualname__}:inputs"
        output_key = f"{method.__qualname__}:outputs"
        self._redis.rpush(input_key, str(args))
        output = method(self, *args, **kwargs)
        self._redis.rpush(output_key, str(output))
        return output
    return wrapper


def replay(method: Callable) -> None:
    """Display the history of calls for a particular function"""
    r = redis.Redis()
    qualname = method.__qualname__
    count = r.get(qualname)
    count = int(count) if count else 0
    
    print(f"{qualname} was called {count} times:")
    
    inputs = r.lrange(f"{qualname}:inputs", 0, -1)
    outputs = r.lrange(f"{qualname}:outputs", 0, -1)
    
    for args, output in zip(inputs, outputs):
        args_str = args.decode('utf-8')
        output_str = output.decode('utf-8')
        print(f"{qualname}(*{args_str}) -> {output_str}")


class Cache:
    """Redis cache implementation with call tracking and replay"""

    def __init__(self):
        """Initialize Redis connection and flush database"""
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    @call_history
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """Store data in Redis with random key"""
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str, fn: Optional[Callable] = None) -> Union[
            str, bytes, int, float]:
        """Retrieve data with optional conversion"""
        data = self._redis.get(key)
        return fn(data) if fn else data

    def get_str(self, key: str) -> str:
        """Get string value (UTF-8 decoded)"""
        return self.get(key, lambda x: x.decode('utf-8'))

    def get_int(self, key: str) -> int:
        """Get integer value"""
        return self.get(key, lambda x: int(x.decode('utf-8')))
