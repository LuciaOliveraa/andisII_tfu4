# app/__init__.py
from flask import Flask, jsonify
from .config import Config
from .db import db, migrate
from .cache import cache
from .events import events
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import time, logging

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    cache.init_app(app)
    events.init_app(app)
    limiter = Limiter(key_func=get_remote_address, app=app, default_limits=[app.config.get('RATE_LIMITS')])

    from .routes.products import bp as products_bp
    from .routes.recipes import recipes_bp
    app.register_blueprint(products_bp, url_prefix='/products')
    app.register_blueprint(recipes_bp, url_prefix='/recipes')

    @app.route("/")
    def index():
        return jsonify({"msg": "API Recetas funcionando 🚀"})

    return app
