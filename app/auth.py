import jwt
import datetime
from flask import current_app, request
from functools import wraps
from app.routes.valet import valet


def gatekeeper(required_scope: str):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            auth = request.headers.get('Authorization')
            if not auth or not auth.startswith('Bearer '):
                return {'message': 'Missing token'}, 401

            token = auth.split(' ', 1)[1]
            data = valet.validate_valet_key(token)

            if not data:
                return {'message': 'Invalid or expired token'}, 401

            scopes = data.get('scopes', [])
            if required_scope not in scopes:
                return {'message': 'Forbidden'}, 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator