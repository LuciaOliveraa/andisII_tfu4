import json
from app.cache import cache

class Events:
    def __init__(self):
        self._redis = None

    def init_app(self, app):
        self._redis = cache.client  # usa el cliente Redis inicializado por Cache

    def publish(self, channel, data):
        message = json.dumps(data)
        self._redis.publish(channel, message)

    def subscribe(self, channel):
        pubsub = self._redis.pubsub()
        pubsub.subscribe(channel)
        for message in pubsub.listen():
            if message["type"] == "message":
                yield json.loads(message["data"])

events = Events()
