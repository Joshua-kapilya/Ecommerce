try:
    import redis
    redis_client = redis.Redis(host='localhost', port=6379, db=0)
    redis_client.ping()  # Test if Redis is actually running
except Exception:
    print("⚠️ Redis not running — using DummyRedis fallback")

    class DummyRedis:
        def __init__(self):
            self.store = {}

        def get(self, key):
            return self.store.get(key)

        def set(self, key, value):
            self.store[key] = value

        def delete(self, key):
            if key in self.store:
                del self.store[key]

        def lrange(self, key, start, end):
            value = self.store.get(key, [])
            return value[start:end + 1]

        def rpush(self, key, *values):
            if key not in self.store:
                self.store[key] = []
            self.store[key].extend(values)

        def exists(self, key):
            return key in self.store

        def ping(self):
            return True

    redis_client = DummyRedis()
