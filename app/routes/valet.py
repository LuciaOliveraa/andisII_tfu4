import time, jwt, os
from app.config import Config
from flask import Blueprint, request, jsonify

bp = Blueprint('valet', __name__)

@bp.route('/token', methods=['POST'])
def get_valet_key():
    data = request.get_json()
    scopes = data.get('scopes', ['recipes:read'])
    token = valet.generate_valet_key(scopes)
    return jsonify({'token': token})


class ValetService:
    @staticmethod
    def generate_valet_key(scopes: list[str]):
        payload = {
            'scopes': scopes,  # ej: ["recipes:read", "recipes:edit"]
            'exp': time.time() + Config.VALET_TOKEN_TTL
        }
        token = jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')
        return token

    @staticmethod
    def validate_valet_key(token: str):
        try:
            data = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
            return data  # devuelve payload decodificado
        except jwt.ExpiredSignatureError:
            return None
        except Exception:
            return None

valet = ValetService()
