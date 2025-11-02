import time, jwt, os
from app.config import Config

class ValetService:
    @staticmethod
    def generate_valet_key(user_id: int, resource: str):
        payload = {
        'sub': user_id,
        'resource': resource,
        'exp': time.time() + Config.VALET_TOKEN_TTL
        }
        token = jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')
        return token

    @staticmethod
    def validate_valet_key(token: str, resource: str):
        try:
            data = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
            return data['resource'] == resource
        except jwt.ExpiredSignatureError:
            return False
        except Exception:
            return False
        