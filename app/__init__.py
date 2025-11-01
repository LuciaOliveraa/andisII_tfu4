from flask import Flask
from .config import Config
from .db import db, migrate
from .cache import cache
from .events import events
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # DB and migrations
    db.init_app(app)
    migrate.init_app(app, db)

    # Cache (redis)
    cache.init_app(app)

    # Events (publisher)
    events.init_app(app)

    # Rate limiter
    #limiter = Limiter(app, key_func=get_remote_address, default_limits=[app.config.get('RATE_LIMITS')])
    limiter = Limiter(key_func=get_remote_address, app=app, default_limits=[app.config.get('RATE_LIMITS')])

    # Blueprints
    from .routes.products import bp as products_bp
    from .routes.recipes import bp as recipes_bp
    from .routes.valet import bp as valet_bp

    app.register_blueprint(products_bp, url_prefix='/products')
    app.register_blueprint(recipes_bp, url_prefix='/recipes')
    app.register_blueprint(valet_bp, url_prefix='/valet')

    # Simple health check
    @app.route('/health')
    def health():
        return {'status': 'ok'}

    return app


# For gunicorn to find
app = create_app()