"""
Customer Data Tools - Flask Application

Main application entry point for the diagnostic tools platform.
"""
import os
from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager
from dotenv import load_dotenv

from src.config.config import Config
from src.api.routes import register_routes
from src.utils.logger import setup_logging, get_logger

# Load environment variables
load_dotenv()

# Configure logging
setup_logging()
logger = get_logger(__name__)


def create_app(config_name='development'):
    """Application factory pattern for Flask app creation"""
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(Config)

    # Enable CORS
    CORS(app)

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'

    @login_manager.user_loader
    def load_user(user_id):
        # TODO: Implement actual user loading from database/session
        # For now, return None (will be implemented in TASK-002)
        return None

    # Register API routes and blueprints
    register_routes(app)

    # Root endpoint
    @app.route('/')
    def index():
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{app.config['APP_NAME']}</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    max-width: 800px;
                    margin: 50px auto;
                    padding: 20px;
                    background: #f8f9fa;
                }}
                .container {{
                    background: white;
                    border-radius: 8px;
                    padding: 40px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                h1 {{
                    color: #183162;
                    margin-bottom: 10px;
                }}
                .subtitle {{
                    color: #666;
                    font-size: 1.1rem;
                    margin-bottom: 30px;
                }}
                .status {{
                    background: #15b79e;
                    color: white;
                    padding: 10px 20px;
                    border-radius: 4px;
                    display: inline-block;
                    margin: 20px 0;
                }}
                .info {{
                    background: #f0f7ff;
                    border-left: 4px solid #ff6227;
                    padding: 15px;
                    margin: 20px 0;
                }}
                .info h3 {{
                    margin-top: 0;
                    color: #183162;
                }}
                ul {{
                    line-height: 1.8;
                }}
                code {{
                    background: #f4f4f4;
                    padding: 2px 6px;
                    border-radius: 3px;
                    font-family: 'Monaco', 'Courier New', monospace;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🔧 {app.config['APP_NAME']}</h1>
                <div class="subtitle">Diagnostic & Troubleshooting Platform for Bookmarked</div>

                <div class="status">✅ Application Running</div>

                <div class="info">
                    <h3>Project Status: Setup Complete</h3>
                    <p>The Customer Data Tools platform is initialized and ready for Phase 1 development.</p>

                    <h4>Next Steps (Phase 1 - Oct 14-17):</h4>
                    <ul>
                        <li>TASK-001: Complete Flask application setup</li>
                        <li>TASK-002: Implement authentication system</li>
                        <li>TASK-003: Build Bookmarked staging DB connector</li>
                        <li>TASK-004: Build Bookmarked production DB connector</li>
                        <li>TASK-005: Create customer integration settings loader</li>
                    </ul>

                    <h4>Target Launch:</h4>
                    <p><strong>October 31, 2025</strong> (17 days)</p>

                    <h4>Quick Links:</h4>
                    <ul>
                        <li><a href="/connections/setup" style="color: #ff6227; font-weight: 600;">🔌 Connection Setup</a> - Configure database and API connections</li>
                        <li><a href="/docs/EXECUTIVE_SUMMARY.html" target="_blank">Executive Summary</a></li>
                        <li><a href="http://localhost:9001/kanban_ui.html" target="_blank">Kanban Board</a></li>
                    </ul>
                </div>

                <p style="margin-top: 30px; color: #666; font-size: 0.9rem;">
                    Running on port {os.getenv('PORT', '6000')} |
                    Environment: {os.getenv('FLASK_ENV', 'development')} |
                    Debug: {app.config['DEBUG']}
                </p>
            </div>
        </body>
        </html>
        """

    # Health check endpoint
    @app.route('/health')
    def health():
        return {
            'status': 'healthy',
            'service': 'customer-data-tools',
            'app_name': app.config['APP_NAME'],
            'environment': os.getenv('FLASK_ENV', 'development'),
            'version': '1.0.0',
            'configured_services': {
                'staging_db': Config.is_configured('staging_db'),
                'production_db': Config.is_configured('production_db'),
                'classlink': Config.is_configured('classlink'),
                'hubspot': Config.is_configured('hubspot')
            }
        }

    logger.info("Application initialized", config=config_name)

    return app


# Development server entry point
if __name__ == '__main__':
    app = create_app()

    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', '6001'))
    debug = os.getenv('DEBUG', 'True').lower() == 'true'

    logger.info("Starting Customer Data Tools", host=host, port=port, debug=debug)

    app.run(host=host, port=port, debug=debug)
