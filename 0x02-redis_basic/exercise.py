#!/usr/bin/env python3
"""
Redis basic exercise module
Contains Cache class for storing data in Redis
"""

import redis
import uuid
from typing import Union, Callable, Optional


class Cache:
    """Cache class for storing data in Redis with random keys"""

    def __init__(self):
        """Initialize Redis client and flush the database"""
        self._redis = redis.Redis()
        self._redis.flushdb()

    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Store data in Redis with a randomly generated key
        
        Args:
            data: Data to store (can be str, bytes, int, or float)
            
        Returns:
            str: The generated key used to store the data
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key
