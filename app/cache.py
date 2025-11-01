import redis
from flask import current_app

class Cache:
def __init__(self):
self._client = None

def init_app(self, app):
url = app.config['REDIS_URL']
self._client = redis.from_url(url, decode_responses=True)

@property
def client(self):
return self._client

def get(self, key):
return self._client.get(key)

def set(self, key, value, ex=None):
self._client.set(key, value, ex=ex)

def delete(self, key):
self._client.delete(key)


cache = Cache()