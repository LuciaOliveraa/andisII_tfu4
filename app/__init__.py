# app/__init__.py
from flask import Flask, jsonify
from .config import Config
from .db import db, migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import time, logging

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    from .cache import cache
    cache.init_app(app)

    from .events import events
    events.init_app(app)
    limiter = Limiter(key_func=get_remote_address, app=app, default_limits=[app.config.get('RATE_LIMITS')])

    from .routes.products import bp as products_bp
    from .routes.recipes import recipes_bp
    app.register_blueprint(products_bp, url_prefix='/products')
    app.register_blueprint(recipes_bp, url_prefix='/recipes')

    from .routes.valet import bp
    app.register_blueprint(bp, url_prefix='/valet') #sensitive

    # register config endpoint blueprint (exposes non-sensitive app config)
    from .routes.config import bp as config_bp
    app.register_blueprint(config_bp, url_prefix='/config')

    @app.route("/")
    def index():
        return jsonify({"msg": "API Recetas funcionando 🚀"})

    return app
