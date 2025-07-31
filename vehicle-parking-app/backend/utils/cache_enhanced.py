"""
Enhanced Redis Cache Utility for Vehicle Parking App
Provides comprehensive caching functionality for API performance optimization
"""

from functools import wraps
import json
import pickle
from datetime import datetime, timedelta
import redis
import hashlib
import logging
from flask import request
from config import Config

logger = logging.getLogger(__name__)

class CacheManager:
    """Enhanced centralized cache management with Redis"""
    
    def __init__(self):
        self.redis_client = None
        self.is_connected = False
        self._init_redis()
    
    def _init_redis(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.Redis(
                host=Config.REDIS_HOST,
                port=Config.REDIS_PORT,
                db=Config.REDIS_DB,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            # Test connection
            self.redis_client.ping()
            self.is_connected = True
            logger.info("✅ Enhanced Redis cache initialized successfully")
        except Exception as e:
            logger.error(f"❌ Redis cache initialization failed: {e}")
            self.redis_client = None
            self.is_connected = False
    
    def is_available(self):
        """Check if Redis cache is available"""
        if not self.redis_client or not self.is_connected:
            return False
        try:
            self.redis_client.ping()
            return True
        except:
            self.is_connected = False
            return False
    
    def get(self, key):
        """Get value from cache with JSON parsing"""
        if not self.is_available():
            return None
        
        try:
            full_key = f"{Config.CACHE_KEY_PREFIX}{key}"
            value = self.redis_client.get(full_key)
            if value is None:
                return None
            
            # Try to parse as JSON, fallback to string
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None
    
    def set(self, key, value, timeout=None):
        """Set value in cache with optional timeout"""
        if not self.is_available():
            return False
        
        try:
            full_key = f"{Config.CACHE_KEY_PREFIX}{key}"
            timeout = timeout or Config.CACHE_DEFAULT_TIMEOUT
            
            # Handle Flask Response objects
            from flask import Response
            if isinstance(value, Response):
                # Extract JSON data from Response object
                try:
                    value = value.get_json()
                except:
                    # If not JSON, skip caching
                    return False
            elif isinstance(value, tuple) and len(value) >= 1:
                # Handle Flask response tuples like (response, status_code)
                if isinstance(value[0], Response):
                    try:
                        value = value[0].get_json()
                    except:
                        return False
            
            # Convert to JSON if possible
            if isinstance(value, (dict, list, tuple)):
                value = json.dumps(value, default=str)
            
            self.redis_client.setex(full_key, timeout, value)
            return True
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    def delete(self, key):
        """Delete key from cache"""
        if not self.is_available():
            return False
        
        try:
            full_key = f"{Config.CACHE_KEY_PREFIX}{key}"
            self.redis_client.delete(full_key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    def delete_pattern(self, pattern):
        """Delete all keys matching pattern"""
        if not self.is_available():
            return False
        
        try:
            full_pattern = f"{Config.CACHE_KEY_PREFIX}{pattern}"
            keys = self.redis_client.keys(full_pattern)
            if keys:
                self.redis_client.delete(*keys)
                logger.debug(f"Deleted {len(keys)} keys matching pattern: {pattern}")
            return True
        except Exception as e:
            logger.error(f"Cache delete pattern error for {pattern}: {e}")
            return False
    
    def get_stats(self):
        """Get detailed cache statistics"""
        if not self.is_available():
            return {'status': 'unavailable'}
        
        try:
            info = self.redis_client.info()
            return {
                'status': 'available',
                'used_memory': info.get('used_memory_human', 'N/A'),
                'connected_clients': info.get('connected_clients', 0),
                'total_commands_processed': info.get('total_commands_processed', 0),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0),
                'hit_rate': round(
                    (info.get('keyspace_hits', 0) / 
                     max(info.get('keyspace_hits', 0) + info.get('keyspace_misses', 0), 1)) * 100, 2
                ) if (info.get('keyspace_hits', 0) + info.get('keyspace_misses', 0)) > 0 else 0
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {'status': 'error', 'error': str(e)}

# Global enhanced cache manager
cache_manager = CacheManager()

# Legacy Cache class for backward compatibility
class Cache:
    """Redis cache utility class - Legacy support"""
    
    @staticmethod
    def get(key, default=None):
        """Get value from cache"""
        result = cache_manager.get(key)
        return result if result is not None else default
    
    @staticmethod
    def set(key, value, timeout=None):
        """Set value in cache"""
        return cache_manager.set(key, value, timeout)
    
    @staticmethod
    def delete(key):
        """Delete key from cache"""
        return cache_manager.delete(key)
    
    @staticmethod
    def exists(key):
        """Check if key exists in cache"""
        return cache_manager.get(key) is not None

# Legacy support for existing code
try:
    redis_client = redis.Redis(
        host=Config.REDIS_HOST,
        port=Config.REDIS_PORT,
        db=Config.REDIS_DB,
        decode_responses=True
    )
    redis_client.ping()
    REDIS_AVAILABLE = True
except Exception as e:
    print(f"Redis connection failed: {e}")
    redis_client = None
    REDIS_AVAILABLE = False

# Cache configuration for different endpoints
CACHE_CONFIG = {
    'parking_lots': {
        'timeout': 300,  # 5 minutes
        'key_prefix': 'lots',
        'invalidate_on': ['lot_created', 'lot_updated', 'lot_deleted']
    },
    'available_spots': {
        'timeout': 60,   # 1 minute (frequently changing)
        'key_prefix': 'spots',
        'invalidate_on': ['reservation_created', 'reservation_updated', 'spot_status_changed']
    },
    'user_reservations': {
        'timeout': 60,   # 1 minute (user needs quick updates)
        'key_prefix': 'reservations',
        'invalidate_on': ['reservation_created', 'reservation_updated', 'reservation_deleted']
    },
    'dashboard_stats': {
        'timeout': 180,  # 3 minutes
        'key_prefix': 'dashboard',
        'invalidate_on': ['reservation_updated', 'reservation_created']
    },
    'lot_occupancy': {
        'timeout': 30,   # 30 seconds (real-time data)
        'key_prefix': 'occupancy',
        'invalidate_on': ['reservation_created', 'reservation_updated']
    },
    'user_dashboard': {
        'timeout': 60,   # 1 minute (user needs quick updates for actions)
        'key_prefix': 'dashboard',
        'invalidate_on': ['reservation_created', 'reservation_updated', 'reservation_deleted']
    },
    'user_parking_history': {
        'timeout': 300,  # 5 minutes (historical data changes less frequently)
        'key_prefix': 'parking_history',
        'invalidate_on': ['reservation_updated', 'reservation_deleted']
    }
}

def generate_cache_key(endpoint, **kwargs):
    """Generate a unique cache key for an endpoint"""
    if endpoint not in CACHE_CONFIG:
        return f"unknown:{endpoint}"
        
    key_parts = [CACHE_CONFIG[endpoint]['key_prefix']]
    
    # Add user context if present
    if 'user_id' in kwargs:
        key_parts.append(f"user_{kwargs['user_id']}")
    
    # Add other parameters
    for key, value in sorted(kwargs.items()):
        if key != 'user_id':
            key_parts.append(f"{key}_{value}")
    
    # Add request parameters for GET requests
    try:
        if request and request.method == 'GET' and request.args:
            query_params = sorted(request.args.items())
            query_hash = hashlib.md5(str(query_params).encode()).hexdigest()[:8]
            key_parts.append(f"query_{query_hash}")
    except:
        pass  # Request context might not be available
    
    return ':'.join(key_parts)

def cached_endpoint(endpoint_name, **cache_kwargs):
    """Decorator for caching API endpoints with performance monitoring"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Skip caching if not available or if Redis/cache is unavailable
            if not cache_manager.is_available():
                return func(*args, **kwargs)
                
            # Skip caching for non-GET requests
            try:
                if request and request.method != 'GET':
                    return func(*args, **kwargs)
            except RuntimeError:
                # Not in request context, execute function directly
                return func(*args, **kwargs)
            
            try:
                # Handle user_specific caching
                cache_key_kwargs = cache_kwargs.copy()
                if cache_kwargs.get('user_specific', False):
                    try:
                        # Try to get user_id from request context
                        if hasattr(request, 'current_user_id'):
                            cache_key_kwargs['user_id'] = request.current_user_id
                        # Remove user_specific flag as it's not needed in cache key
                        cache_key_kwargs.pop('user_specific', None)
                    except:
                        pass  # If user context not available, proceed without user-specific caching
                
                # Generate cache key
                cache_key = generate_cache_key(endpoint_name, **cache_key_kwargs)
                
                # Try to get from cache
                start_time = datetime.now()
                cached_result = cache_manager.get(cache_key)
                
                if cached_result is not None:
                    cache_time = (datetime.now() - start_time).total_seconds() * 1000
                    logger.debug(f"✅ Cache HIT for {cache_key} ({cache_time:.2f}ms)")
                    # Return cached result as JSON response
                    from flask import jsonify
                    return jsonify(cached_result)
                
                # Execute function and cache result
                logger.debug(f"❌ Cache MISS for {cache_key}")
                result = func(*args, **kwargs)
                
                # Cache the result
                if endpoint_name in CACHE_CONFIG:
                    timeout = CACHE_CONFIG[endpoint_name]['timeout']
                    cache_manager.set(cache_key, result, timeout)
                
                exec_time = (datetime.now() - start_time).total_seconds() * 1000
                logger.debug(f"⏱️  Function executed in {exec_time:.2f}ms")
                
                return result
                
            except Exception as e:
                # If caching fails, execute function directly
                logger.warning(f"Cache error for {endpoint_name}: {e}")
                return func(*args, **kwargs)
        return wrapper
    return decorator

def invalidate_cache(pattern):
    """Invalidate cache based on pattern"""
    if not cache_manager.is_available():
        return
        
    try:
        logger.info(f"🗑️ Invalidating cache pattern: {pattern}")
        
        # Use the cache manager to delete pattern
        deleted_count = cache_manager.delete_pattern(pattern)
        
        logger.info(f"Invalidated {deleted_count} cache entries for pattern: {pattern}")
        return deleted_count
        
    except Exception as e:
        logger.warning(f"Failed to invalidate cache pattern {pattern}: {e}")
        return 0

def warm_cache():
    """Pre-populate cache with frequently accessed data"""
    logger.info("🔥 Warming up cache...")
    
    try:
        from models.parking_lot import ParkingLot
        from models.parking_spot import ParkingSpot
        
        # Cache parking lots
        lots = ParkingLot.query.all()
        lots_data = [lot.to_dict() for lot in lots]
        cache_manager.set('lots:all', lots_data, CACHE_CONFIG['parking_lots']['timeout'])
        
        # Cache available spots for each lot
        for lot in lots:
            available_spots = ParkingSpot.query.filter_by(
                lot_id=lot.id, 
                status='A'
            ).count()
            cache_manager.set(
                f'spots:lot_{lot.id}:available', 
                available_spots, 
                CACHE_CONFIG['available_spots']['timeout']
            )
        
        logger.info("✅ Cache warmed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Cache warming failed: {e}")
        return False

# Performance monitoring decorators
def cache_performance(func):
    """Decorator to monitor cache performance"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = datetime.now()
        result = func(*args, **kwargs)
        exec_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # Log performance metrics
        logger.debug(f"Function {func.__name__} executed in {exec_time:.2f}ms")
        
        return result
    return wrapper
