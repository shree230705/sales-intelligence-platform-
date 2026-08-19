"""
Application factory.

We use the factory pattern (`create_app`) instead of a single global Flask
instance for two reasons:

1. Testing — pytest can call `create_app("testing")` to get an app wired to
   a separate test database, completely isolated from dev/prod data.
2. Avoiding circular imports — blueprints import from `app.services` and
   `app.utils`, and those modules never need to import the Flask `app`
   object directly, since everything is registered here instead.
"""

import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

from app.config import config_by_name
from app.utils.db import init_app as init_db

# Load variables from .env into the process environment before Config
# classes read them.
load_dotenv()


def create_app(env_name=None):
    env_name = env_name or os.environ.get("FLASK_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(config_by_name[env_name]())

    # --- CORS ---
    CORS(app, origins=app.config["CORS_ORIGINS"], supports_credentials=True)

    # --- Database teardown hook ---
    init_db(app)

    # --- Blueprints ---
    register_blueprints(app)

    return app


def register_blueprints(app):
    from app.routes.health_routes import health_bp
    from app.routes.debug_routes import debug_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(debug_bp)

    # Registered in later phases:
    # from app.routes.auth_routes import auth_bp
    # from app.routes.lead_routes import lead_bp
    # from app.routes.customer_routes import customer_bp
    # from app.routes.opportunity_routes import opportunity_bp
    # from app.routes.followup_routes import followup_bp
    # from app.routes.proposal_routes import proposal_bp
    # from app.routes.competitor_routes import competitor_bp
    # from app.routes.target_routes import target_bp
    # from app.routes.analytics_routes import analytics_bp
    # from app.routes.notification_routes import notification_bp
    # from app.routes.ml_routes import ml_bp
