#!/usr/bin/env python3
"""
Redis caching module with call history tracking
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
        """Wrapper function that records inputs and outputs"""
        input_key = f"{method.__qualname__}:inputs"
        output_key = f"{method.__qualname__}:outputs"
        
        # Store input arguments
        self._redis.rpush(input_key, str(args))
        
        # Execute method and store output
        output = method(self, *args, **kwargs)
        self._redis.rpush(output_key, str(output))
        
        return output
    return wrapper


class Cache:
    """Redis cache implementation with call tracking"""

    def __init__(self):
        """Initialize Redis connection and flush database"""
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    @call_history
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Store data in Redis with random key
        Args:
            data: Data to store (str/bytes/int/float)
        Returns:
            str: Generated key
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str, fn: Optional[Callable] = None) -> Union[str, bytes, int, float]:
        """
        Retrieve data with optional conversion
        Args:
            key: Redis key
            fn: Conversion function
        Returns:
            Converted or raw data
        """
        data = self._redis.get(key)
        return fn(data) if fn else data

    def get_str(self, key: str) -> str:
        """Get string value (UTF-8 decoded)"""
        return self.get(key, lambda x: x.decode('utf-8'))

    def get_int(self, key: str) -> int:
        """Get integer value"""
        return self.get(key, lambda x: int(x.decode('utf-8')))
