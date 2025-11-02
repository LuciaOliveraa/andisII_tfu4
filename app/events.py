# import redis
# from flask import current_app
# import json

# class Events:
#     def __init__(self):
#         self._client = None

#     def init_app(self, app):
#         self._client = redis.from_url(app.config['REDIS_URL'], decode_responses=True)

#     def publish(self, channel, event: dict):
#         payload = json.dumps(event)
#         self._client.publish(channel, payload)


# events = Events()

# app/events.py

# import json
# from app.cache import cache

# def publish(channel: str, data: dict):
#     """
#     Publisher: sends an event message to a Redis channel.
#     """
#     message = json.dumps(data)
#     cache.publish(channel, message)


# def subscribe(channel: str):
#     """
#     Subscriber: yields messages as they arrive from the given Redis channel.
#     """
#     pubsub = cache.pubsub()
#     pubsub.subscribe(channel)
#     print(f"[Subscriber] Subscribed to channel: {channel}")
#     for message in pubsub.listen():
#         if message['type'] == 'message':
#             yield json.loads(message['data'])


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
