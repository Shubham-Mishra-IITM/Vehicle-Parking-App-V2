from functools import wraps
import json
import pickle
from datetime import timedelta
import redis
from config import Config

# Initialize Redis connection
try:
    redis_client = redis.Redis(
        host=Config.REDIS_HOST,
        port=Config.REDIS_PORT,
        db=Config.REDIS_DB,
        decode_responses=True
    )
    # Test connection
    redis_client.ping()
    REDIS_AVAILABLE = True
except Exception as e:
    print(f"Redis connection failed: {e}")
    redis_client = None
    REDIS_AVAILABLE = False

class Cache:
    """Redis cache utility class"""
    
    @staticmethod
    def get(key, default=None):
        """Get value from cache"""
        if not REDIS_AVAILABLE:
            return default
        
        try:
            value = redis_client.get(f"{Config.CACHE_KEY_PREFIX}{key}")
            if value is None:
                return default
            return json.loads(value)
        except Exception as e:
            print(f"Cache get error: {e}")
            return default
    
    @staticmethod
    def set(key, value, timeout=None):
        """Set value in cache"""
        if not REDIS_AVAILABLE:
            return False
        
        try:
            timeout = timeout or Config.CACHE_DEFAULT_TIMEOUT
            serialized_value = json.dumps(value, default=str)
            return redis_client.setex(
                f"{Config.CACHE_KEY_PREFIX}{key}",
                timeout,
                serialized_value
            )
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    @staticmethod
    def delete(key):
        """Delete value from cache"""
        if not REDIS_AVAILABLE:
            return False
        
        try:
            return redis_client.delete(f"{Config.CACHE_KEY_PREFIX}{key}")
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False
    
    @staticmethod
    def clear_pattern(pattern):
        """Clear cache keys matching pattern"""
        if not REDIS_AVAILABLE:
            return False
        
        try:
            keys = redis_client.keys(f"{Config.CACHE_KEY_PREFIX}{pattern}")
            if keys:
                return redis_client.delete(*keys)
            return True
        except Exception as e:
            print(f"Cache clear pattern error: {e}")
            return False
    
    @staticmethod
    def exists(key):
        """Check if key exists in cache"""
        if not REDIS_AVAILABLE:
            return False
        
        try:
            return redis_client.exists(f"{Config.CACHE_KEY_PREFIX}{key}")
        except Exception as e:
            print(f"Cache exists error: {e}")
            return False
    
    @staticmethod
    def get_many(keys):
        """Get multiple values from cache"""
        if not REDIS_AVAILABLE:
            return {}
        
        try:
            cache_keys = [f"{Config.CACHE_KEY_PREFIX}{key}" for key in keys]
            values = redis_client.mget(cache_keys)
            result = {}
            for i, key in enumerate(keys):
                if values[i] is not None:
                    try:
                        result[key] = json.loads(values[i])
                    except json.JSONDecodeError:
                        result[key] = values[i]
                else:
                    result[key] = None
            return result
        except Exception as e:
            print(f"Cache get_many error: {e}")
            return {}
    
    @staticmethod
    def set_many(mapping, timeout=None):
        """Set multiple values in cache"""
        if not REDIS_AVAILABLE:
            return False
        
        try:
            timeout = timeout or Config.CACHE_DEFAULT_TIMEOUT
            pipe = redis_client.pipeline()
            
            for key, value in mapping.items():
                serialized_value = json.dumps(value, default=str)
                pipe.setex(
                    f"{Config.CACHE_KEY_PREFIX}{key}",
                    timeout,
                    serialized_value
                )
            
            return pipe.execute()
        except Exception as e:
            print(f"Cache set_many error: {e}")
            return False

def cache_result(timeout=None, key_func=None):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default key generation
                cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Try to get from cache
            cached_result = Cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            Cache.set(cache_key, result, timeout)
            return result
        
        return wrapper
    return decorator

def invalidate_cache_pattern(pattern):
    """Helper to invalidate cache patterns"""
    return Cache.clear_pattern(pattern)

def get_user_cache_key(user_id, suffix=""):
    """Generate cache key for user-specific data"""
    return f"user:{user_id}:{suffix}" if suffix else f"user:{user_id}"

def get_parking_lot_cache_key(lot_id, suffix=""):
    """Generate cache key for parking lot data"""
    return f"parking_lot:{lot_id}:{suffix}" if suffix else f"parking_lot:{lot_id}"

def get_parking_spot_cache_key(spot_id, suffix=""):
    """Generate cache key for parking spot data"""
    return f"parking_spot:{spot_id}:{suffix}" if suffix else f"parking_spot:{spot_id}"

# Cache timeouts in seconds
CACHE_TIMEOUTS = {
    'parking_lots': 300,  # 5 minutes
    'parking_spots': 60,  # 1 minute (changes frequently)
    'user_dashboard': 180,  # 3 minutes
    'admin_dashboard': 120,  # 2 minutes
    'reservations': 30,  # 30 seconds (very dynamic)
    'user_profile': 600,  # 10 minutes
    'statistics': 300,  # 5 minutes
}
