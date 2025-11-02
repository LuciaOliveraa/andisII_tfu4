import time, jwt, os
from app.config import Config
from flask import Blueprint, request, jsonify
from ..valet import valet

bp = Blueprint('recipes', __name__)

@bp.route('/valet', methods=['POST'])
def get_valet_key():
    data = request.get_json()
    #user_id = data.get('user_id')
    scopes = data.get('scopes', ['recipes:read'])
    token = valet.generate_valet_key(scopes)
    return {'token': token}


class ValetService:
    @staticmethod
    def generate_valet_key(scopes: list[str]):
        payload = {
            #'sub': user_id,
            'scopes': scopes,  # ej: ["recipes:read", "recipes:edit"]
            'exp': time.time() + Config.VALET_TOKEN_TTL
        }
        token = jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')
        return token
    
    # def generate_valet_key(user_id: int, resource: str):
    #     payload = {
    #     'sub': user_id,
    #     'resource': resource,
    #     'exp': time.time() + Config.VALET_TOKEN_TTL
    #     }
    #     token = jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')
    #     return token

    @staticmethod
    def validate_valet_key(token: str):
        try:
            data = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
            return data  # devuelve payload decodificado
        except jwt.ExpiredSignatureError:
            return None
        except Exception:
            return None
    # def validate_valet_key(token: str, resource: str):
    #     try:
    #         data = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
    #         return data['resource'] == resource
    #     except jwt.ExpiredSignatureError:
    #         return False
    #     except Exception:
    #         return False

valet = ValetService()
