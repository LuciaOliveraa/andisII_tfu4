import redis
from flask import current_app
import json

class Events:
def __init__(self):
self._client = None

def init_app(self, app):
self._client = redis.from_url(app.config['REDIS_URL'], decode_responses=True)

def publish(self, channel, event: dict):
payload = json.dumps(event)
self._client.publish(channel, payload)


events = Events()