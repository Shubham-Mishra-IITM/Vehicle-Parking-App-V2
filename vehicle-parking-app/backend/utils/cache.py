from redis import Redis

class Cache:
    def __init__(self):
        self.redis = Redis(host='localhost', port=6379, db=0)

    def set(self, key, value, timeout=None):
        self.redis.set(key, value, ex=timeout)

    def get(self, key):
        return self.redis.get(key)

    def delete(self, key):
        self.redis.delete(key)

    def exists(self, key):
        return self.redis.exists(key)