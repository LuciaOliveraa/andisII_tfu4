#!/usr/bin/env python3
"""Demo script for architectural patterns implemented in the project.

This script demonstrates:
- Rate limiting (Flask-Limiter) via repeated requests to the app's index route
- Retry strategy using tenacity
- Publisher-Subscriber with Redis
- Cache-aside pattern using the project's cache
- Valet token creation/validation (JWT)
- Gatekeeper decorator usage (permission check)
- Reading configuration (external config via environment variables)

Notes:
- This script expects Redis (and optionally Postgres) to be reachable using the project's
`REDIS_URL` and `DATABASE_URL` environment variables. Run via `docker-compose up` for full stack.
"""
import threading
import time
import os
import json

from app import create_app
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from tenacity import retry, stop_after_attempt, wait_fixed
import redis

from app.cache import cache
from app.events import events
from app.auth import create_valet_token, decode_token, gatekeeper


def demo_rate_limiter(app):
    print('\n--- Rate limiter demo ---')
    # Re-init limiter with a low limit for demo
    Limiter(app=app, key_func=get_remote_address, default_limits=['3/min'])

    client = app.test_client()
    for i in range(1, 6):
        resp = client.get('/')
        status = resp.status_code
        print(f'Attempt {i}: status={status} data={resp.get_data(as_text=True).strip()}')
        time.sleep(0.2)


def demo_retry(app):
    print('\n--- Retry demo ---')
    # Use the app's test client to call the POST /products endpoint which
    # has a simulated transient error. The route is decorated with
    # retry_on_exception so failed attempts will be retried server-side.
    client = app.test_client()
    payload = {'name': 'Retry Demo Product', 'unit': 'pcs'}

    for i in range(1, 6):
        resp = client.post('/products/', json=payload)
        status = resp.status_code
        body = resp.get_data(as_text=True).strip()
        print(f'Attempt {i}: status={status} data={body}')
        time.sleep(0.2)

def demo_cache_aside(app):
    print('\n--- Cache-aside demo (via endpoints + direct cache) ---')
    client = app.test_client()
    key = 'demo:product:42'

    # 1) Try to GET via endpoint (should be a miss initially)
    resp = client.get(f'/products/cache/{key}')
    print('  GET /products/cache/{key} ->', resp.status_code, resp.get_data(as_text=True).strip())

    # 2) Set value via endpoint
    value = json.dumps({'id': 42, 'name': 'Demo Product', 'ts': time.time()})
    resp = client.post('/products/cache', json={'key': key, 'value': value, 'ex': app.config.get('CACHE_DEFAULT_TTL', 60)})
    print('  POST /products/cache ->', resp.status_code, resp.get_data(as_text=True).strip())

    # 3) Get again via endpoint (should be a hit)
    resp = client.get(f'/products/cache/{key}')
    print('  GET /products/cache/{key} ->', resp.status_code, resp.get_data(as_text=True).strip())

    # 4) Demonstrate direct cache access from the app
    with app.app_context():
        cached = cache.get(key)
        print('  direct cache.get ->', cached)


def demo_pubsub(app):
    print('\n--- Pub/Sub demo (Redis) ---')
    channel = 'demo_channel'

    def subscriber():
        # create a direct redis client for subscription (so pubsub.listen() blocks here)
        r = redis.from_url(app.config['REDIS_URL'], decode_responses=True)
        ps = r.pubsub()
        ps.subscribe(channel)
        print('  subscriber: subscribed, waiting for a message...')
        for msg in ps.listen():
            if msg and msg.get('type') == 'message':
                print('  subscriber: got message ->', msg.get('data'))
                break
        ps.close()

    t = threading.Thread(target=subscriber, daemon=True)
    t.start()

    # give subscriber a moment to subscribe
    time.sleep(0.5)
    # publish via the project's events wrapper
    try:
        events.publish(channel, {'msg': 'hello from demo', 'ts': time.time()})
        print('  publisher: published message via events.publish')
    except Exception as e:
        print('  publisher: failed to publish via events.publish ->', e)

    # give some time for message delivery
    t.join(timeout=5)


def demo_valet_and_gatekeeper(app):
    print('\n--- Valet token & Gatekeeper demo ---')
    with app.app_context():
        # create a valet token with scopes
        payload = {'sub': 1, 'scopes': ['read:recipes', 'write:products']}
        token = create_valet_token(payload, expires_seconds=30)
        print('  generated token:', token)
        decoded = decode_token(token)
        print('  decoded token payload:', decoded)

        # demonstrate gatekeeper decorator using a test request context
        @gatekeeper('read:recipes')
        def protected():
            return {'message': 'access granted'}

        # simulate a request with the token in header
        with app.test_request_context('/', headers={'Authorization': f'Bearer {token}'}):
            resp = protected()
            print('  protected() response:', resp)


def demo_external_config():

    print('\n--- External config demo ---')
    # create an app instance and show config values pulled from the
    # application's config object (which is populated from the
    # project's Config class / environment variables)
    app = create_app()

    # Print a few non-sensitive config values
    print('  RATE_LIMITS =', app.config.get('RATE_LIMITS'))
    print('  CACHE_DEFAULT_TTL =', app.config.get('CACHE_DEFAULT_TTL'))
    print('  REDIS_URL =', app.config.get('REDIS_URL'))

    # Demonstrate retrieving the same values via an endpoint (if available)
    client = app.test_client()
    try:
        resp = client.get('/config/')
        print('  GET /config ->', resp.status_code, resp.get_data(as_text=True).strip())
    except Exception as e:
        print('  GET /config failed ->', e)


def main():
    print('Starting demo script... (this will use your app config and Redis if available)')
    app = create_app()

    # show config value (external config store demo)
    demo_external_config()

    # Rate limiter demo (uses Flask test client)
    demo_rate_limiter(app)

    # tenacity retry demo
    demo_retry(app)

    # cache-aside demo
    demo_cache_aside(app)

    # pub/sub demo (requires Redis reachable at REDIS_URL)
    try:
        demo_pubsub(app)
    except Exception as e:
        print('  Pub/Sub demo failed (Redis may be unavailable):', e)

    # valet token and gatekeeper demo
    demo_valet_and_gatekeeper(app)

    print('\nDemo finished.')


if __name__ == '__main__':
    main()
