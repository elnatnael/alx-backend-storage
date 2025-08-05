#!/usr/bin/env python3
"""
Web cache and tracker implementation
"""

import requests
import redis
from typing import Callable
from functools import wraps

# Initialize Redis connection
redis_client = redis.Redis()


def track_and_cache(method: Callable) -> Callable:
    """
    Decorator to track URL accesses and cache responses
    with 10-second expiration
    """
    @wraps(method)
    def wrapper(url: str) -> str:
        # Track URL access count
        count_key = f"count:{url}"
        redis_client.incr(count_key)

        # Check cache first
        cache_key = f"cache:{url}"
        cached_content = redis_client.get(cache_key)
        if cached_content:
            return cached_content.decode('utf-8')

        # Get fresh content if not in cache
        content = method(url)
        
        # Cache with expiration
        redis_client.setex(cache_key, 10, content)
        return content
    return wrapper


@track_and_cache
def get_page(url: str) -> str:
    """
    Get HTML content of a URL with caching and access tracking
    Args:
        url: URL to fetch
    Returns:
        str: HTML content
    """
    response = requests.get(url)
    return response.text


if __name__ == "__main__":
    # Test with slow URL
    slow_url = "http://slowwly.robertomurray.co.uk/delay/3000/url/http://www.google.com"
    print(get_page(slow_url))  # First call - slow
    print(get_page(slow_url))  # Second call - fast (from cache)
    print(f"Access count: {redis_client.get(f'count:{slow_url}').decode('utf-8')}")
