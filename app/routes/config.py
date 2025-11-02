from flask import Blueprint, current_app, jsonify
import re

bp = Blueprint('config', __name__)


@bp.route('/', methods=['GET'])
def show_config():
    """Return a small, non-sensitive subset of app configuration.

    Sensitive fields (like SECRET_KEY) are omitted or masked.
    This endpoint demonstrates reading configuration from the running
    Flask app (i.e. an "external configuration store" for the demo).
    """
    cfg = {
        'RATE_LIMITS': current_app.config.get('RATE_LIMITS'),
        'CACHE_DEFAULT_TTL': current_app.config.get('CACHE_DEFAULT_TTL'),
        'REDIS_URL': current_app.config.get('REDIS_URL'),
        'SQLALCHEMY_DATABASE_URI': current_app.config.get('SQLALCHEMY_DATABASE_URI'),
    }

    # Mask credentials in SQLALCHEMY_DATABASE_URI (user:pass -> user:****)
    uri = cfg.get('SQLALCHEMY_DATABASE_URI') or ''
    if uri:
        cfg['SQLALCHEMY_DATABASE_URI'] = re.sub(r'://([^:@]+):([^@]+)@', r'://\1:****@', uri)

    # Don't return SECRET_KEY
    return jsonify(cfg)
