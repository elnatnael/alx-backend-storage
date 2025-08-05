#!/usr/bin/env python3
"""
Web cache and tracker implementation with Redis
"""

import requests
import redis
from typing import Callable
from functools import wraps

redis_client = redis.Redis()


def track_and_cache(method: Callable) -> Callable:
    """
    Decorator to track URL accesses and cache responses
    with 10-second expiration
    """
    @wraps(method)
    def wrapper(url: str) -> str:
        count_key = f"count:{url}"
        cache_key = f"cache:{url}"

        redis_client.incr(count_key)
        cached_content = redis_client.get(cache_key)
        if cached_content:
            return cached_content.decode('utf-8')

        content = method(url)
        redis_client.setex(cache_key, 10, content)
        return content
    return wrapper


@track_and_cache
def get_page(url: str) -> str:
    """
    Get HTML content of a URL with caching and tracking
    Args:
        url: URL to fetch
    Returns:
        str: HTML content
    """
    response = requests.get(url)
    return response.text


def test_cache_expiration():
    """Test cache expiration functionality"""
    test_url = "http://google.com"
    
    # First call - should cache
    get_page(test_url)
    assert redis_client.get(f"cache:{test_url}") is not None
    
    # Wait for cache to expire
    import time
    time.sleep(11)
    
    # Verify cache is cleared
    assert redis_client.get(f"cache:{test_url}") is None


def test_count_increment():
    """Test access count increments"""
    test_url = "http://example.com"
    count_key = f"count:{test_url}"
    redis_client.delete(count_key)  # Reset counter
    
    get_page(test_url)
    assert int(redis_client.get(count_key)) == 1
    
    get_page(test_url)
    assert int(redis_client.get(count_key)) == 2


if __name__ == "__main__":
    test_cache_expiration()
    test_count_increment()
    print("All tests passed!")
