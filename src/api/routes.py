"""
API Route registration for Customer Data Tools
"""
from flask import Flask


def register_routes(app: Flask):
    """
    Register all API routes and blueprints

    Args:
        app: Flask application instance
    """
    # Import and register blueprints
    from src.routes.connections import connections_bp
    from src.routes.hubspot_auth import hubspot_auth_bp

    app.register_blueprint(connections_bp)
    app.register_blueprint(hubspot_auth_bp)

    # Additional blueprints (to be implemented):
    # from src.routes.dashboard import dashboard_bp
    # from src.routes.tools import tools_bp
    # from src.routes.settings import settings_bp
    # from src.routes.auth import auth_bp
    #
    # app.register_blueprint(auth_bp, url_prefix='/auth')
    # app.register_blueprint(dashboard_bp, url_prefix='/')
    # app.register_blueprint(tools_bp, url_prefix='/tools')
    # app.register_blueprint(settings_bp, url_prefix='/settings')
