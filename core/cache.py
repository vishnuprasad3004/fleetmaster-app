"""Redis caching utilities."""

import json
import pickle
from typing import Any, Optional, Dict, List
from datetime import datetime, timedelta
import redis.asyncio as redis
from functools import wraps

from app.config.settings import settings


class CacheService:
    """Redis cache service."""
    
    def __init__(self):
        self.redis_client = None
        
    async def connect(self):
        """Initialize Redis connection."""
        self.redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=False
        )
    
    async def disconnect(self):
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.close()
    
    async def get(self, key: str) -> Any:
        """Get value from cache."""
        try:
            if not self.redis_client:
                await self.connect()
            
            value = await self.redis_client.get(key)
            if value:
                return pickle.loads(value)
            return None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set value in cache with TTL."""
        try:
            if not self.redis_client:
                await self.connect()
            
            ttl = ttl or settings.REDIS_CACHE_TTL
            serialized = pickle.dumps(value)
            await self.redis_client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        try:
            if not self.redis_client:
                await self.connect()
            
            await self.redis_client.delete(key)
            return True
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False
    
    async def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern."""
        try:
            if not self.redis_client:
                await self.connect()
            
            keys = await self.redis_client.keys(pattern)
            if keys:
                return await self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            print(f"Cache delete pattern error: {e}")
            return 0
    
    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        try:
            if not self.redis_client:
                await self.connect()
            
            return bool(await self.redis_client.exists(key))
        except Exception as e:
            print(f"Cache exists error: {e}")
            return False
    
    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment counter."""
        try:
            if not self.redis_client:
                await self.connect()
            
            return await self.redis_client.incrby(key, amount)
        except Exception as e:
            print(f"Cache increment error: {e}")
            return 0
    
    async def expire(self, key: str, ttl: int) -> bool:
        """Set expiry for key."""
        try:
            if not self.redis_client:
                await self.connect()
            
            return await self.redis_client.expire(key, ttl)
        except Exception as e:
            print(f"Cache expire error: {e}")
            return False


# Global cache instance
cache = CacheService()


def cache_key(*args, **kwargs) -> str:
    """Generate cache key from arguments."""
    key_parts = []
    
    # Add positional arguments
    for arg in args:
        if isinstance(arg, (str, int, float)):
            key_parts.append(str(arg))
        else:
            key_parts.append(str(hash(str(arg))))
    
    # Add keyword arguments (sorted for consistency)
    for k, v in sorted(kwargs.items()):
        if isinstance(v, (str, int, float, bool)):
            key_parts.append(f"{k}:{v}")
        else:
            key_parts.append(f"{k}:{hash(str(v))}")
    
    return ":".join(key_parts)


def cached(ttl: int = None, key_prefix: str = ""):
    """Decorator for caching function results."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key_str = f"{key_prefix}{func.__name__}:" + cache_key(*args, **kwargs)
            
            # Try to get from cache
            cached_result = await cache.get(cache_key_str)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache.set(cache_key_str, result, ttl)
            
            return result
        return wrapper
    return decorator


class CacheKeys:
    """Centralized cache key definitions."""
    
    # Vehicle caches
    VEHICLE_STATS = "vehicle:stats:{owner_id}"
    VEHICLE_LIST = "vehicle:list:{owner_id}:{status}:{skip}:{limit}"
    VEHICLE_DETAIL = "vehicle:detail:{vehicle_id}"
    VEHICLES_EXPIRED_DOCS = "vehicle:expired_docs:{owner_id}"
    VEHICLES_SERVICE_DUE = "vehicle:service_due:{owner_id}"
    
    # Driver caches  
    DRIVER_STATS = "driver:stats:{owner_id}"
    DRIVER_LIST = "driver:list:{owner_id}:{status}:{skip}:{limit}"
    DRIVER_DETAIL = "driver:detail:{driver_id}"
    DRIVERS_EXPIRED_LICENSE = "driver:expired_license:{owner_id}"
    DRIVERS_LICENSE_EXPIRING = "driver:license_expiring:{owner_id}:{days}"
    
    # Trip caches
    TRIP_STATS = "trip:stats:{owner_id}:{days}"
    TRIP_LIST = "trip:list:{owner_id}:{status}:{skip}:{limit}"
    TRIP_DETAIL = "trip:detail:{trip_id}"
    ACTIVE_TRIPS = "trip:active:{owner_id}"
    PROFIT_ANALYSIS = "trip:profit_analysis:{owner_id}:{days}"
    
    # Dashboard caches
    DASHBOARD_STATS = "dashboard:stats:{owner_id}"
    DASHBOARD_ALERTS = "dashboard:alerts:{owner_id}"
    RECENT_ACTIVITY = "dashboard:activity:{owner_id}"
    
    # Rate limiting
    RATE_LIMIT_USER = "rate_limit:user:{user_id}:{endpoint}"
    RATE_LIMIT_IP = "rate_limit:ip:{ip_address}:{endpoint}"
    
    # Session management
    USER_SESSION = "session:{user_id}:{session_token}"
    LOGIN_ATTEMPTS = "login_attempts:{email}:{ip}"


class CacheInvalidator:
    """Helper for cache invalidation patterns."""
    
    @staticmethod
    async def invalidate_user_data(owner_id: str):
        """Invalidate all user-related caches."""
        patterns = [
            f"vehicle:*:{owner_id}*",
            f"driver:*:{owner_id}*", 
            f"trip:*:{owner_id}*",
            f"dashboard:*:{owner_id}*"
        ]
        
        for pattern in patterns:
            await cache.delete_pattern(pattern)
    
    @staticmethod
    async def invalidate_vehicle_caches(owner_id: str, vehicle_id: str = None):
        """Invalidate vehicle-related caches."""
        patterns = [
            f"vehicle:*:{owner_id}*",
            f"dashboard:*:{owner_id}*"
        ]
        
        if vehicle_id:
            patterns.append(f"vehicle:detail:{vehicle_id}")
            patterns.append(f"trip:*:{vehicle_id}*")
        
        for pattern in patterns:
            await cache.delete_pattern(pattern)
    
    @staticmethod
    async def invalidate_driver_caches(owner_id: str, driver_id: str = None):
        """Invalidate driver-related caches."""
        patterns = [
            f"driver:*:{owner_id}*",
            f"dashboard:*:{owner_id}*"
        ]
        
        if driver_id:
            patterns.append(f"driver:detail:{driver_id}")
            patterns.append(f"trip:*:{driver_id}*")
        
        for pattern in patterns:
            await cache.delete_pattern(pattern)
    
    @staticmethod
    async def invalidate_trip_caches(owner_id: str, trip_id: str = None):
        """Invalidate trip-related caches."""
        patterns = [
            f"trip:*:{owner_id}*",
            f"dashboard:*:{owner_id}*"
        ]
        
        if trip_id:
            patterns.append(f"trip:detail:{trip_id}")
        
        for pattern in patterns:
            await cache.delete_pattern(pattern)