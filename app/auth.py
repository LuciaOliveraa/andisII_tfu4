import jwt
import datetime
from flask import current_app, request
from functools import wraps
from app.valet import valet


# def create_valet_token(payload: dict, expires_seconds: int = 60):
#     now = datetime.datetime.utcnow()
#     payload = payload.copy()
#     payload.update({'iat': now, 'exp': now + datetime.timedelta(seconds=expires_seconds)})
#     token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
#     return token


# def decode_token(token: str):
#     try:
#         data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
#         return data
#     except jwt.ExpiredSignatureError:
#         return None
#     except Exception:
#         return None


# Gatekeeper decorator - simple permission check
def gatekeeper(required_scope: str):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            auth = request.headers.get('Authorization')
            if not auth or not auth.startswith('Bearer '):
                return {'message': 'Missing token'}, 401

            token = auth.split(' ', 1)[1]
            data = valet.validate_valet_key(token)
            #data = decode_token(token)

            if not data:
                return {'message': 'Invalid or expired token'}, 401

            scopes = data.get('scopes', [])
            if required_scope not in scopes:
                return {'message': 'Forbidden'}, 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator
