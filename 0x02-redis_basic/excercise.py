#!/usr/bin/env python3
"""
Redis basic exercise module
Contains Cache class for storing and retrieving typed data in Redis
"""

import redis
import uuid
from typing import Union, Callable, Optional


class Cache:
    """Cache class for storing and retrieving data in Redis with type conversion"""

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

    def get(
        self, 
        key: str, 
        fn: Optional[Callable[[bytes], Union[str, int, float]] = None
    ) -> Union[str, bytes, int, float, None]:
        """
        Retrieve data from Redis and optionally apply a conversion function
        
        Args:
            key: Key to retrieve
            fn: Optional callable to convert the data from bytes
            
        Returns:
            Data in original bytes or converted format, None if key doesn't exist
        """
        data = self._redis.get(key)
        if data is None:
            return None
        return fn(data) if fn else data

    def get_str(self, key: str) -> str:
        """
        Retrieve a string from Redis (automatically UTF-8 decoded)
        
        Args:
            key: Key to retrieve
            
        Returns:
            str: Decoded UTF-8 string
        """
        return self.get(key, lambda d: d.decode('utf-8'))

    def get_int(self, key: str) -> int:
        """
        Retrieve an integer from Redis
        
        Args:
            key: Key to retrieve
            
        Returns:
            int: Converted integer
        """
        return self.get(key, lambda d: int(d.decode('utf-8')))
