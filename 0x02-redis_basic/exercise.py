#!/usr/bin/env python3
"""
Redis caching module with type conversion support
"""

import redis
import uuid
from typing import Union, Callable, Optional


class Cache:
    """Redis cache implementation with type conversion"""

    def __init__(self):
        """Initialize Redis connection and flush database"""
        self._redis = redis.Redis()
        self._redis.flushdb()

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
        if fn:
            return fn(data)
        return data

    def get_str(self, key: str) -> str:
        """Get string value (UTF-8 decoded)"""
        return self.get(key, lambda x: x.decode('utf-8'))

    def get_int(self, key: str) -> int:
        """Get integer value"""
        return self.get(key, lambda x: int(x.decode('utf-8')))
