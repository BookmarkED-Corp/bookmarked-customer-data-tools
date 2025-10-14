"""
Configuration management for Customer Data Tools
"""
import os
from typing import Optional


class Config:
    """Application configuration"""

    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    APP_NAME = os.getenv('APP_NAME', 'Customer Data Tools')

    # Session Configuration
    SESSION_TIMEOUT_MINUTES = int(os.getenv('SESSION_TIMEOUT_MINUTES', '60'))
    PERMANENT_SESSION_LIFETIME = SESSION_TIMEOUT_MINUTES * 60

    # Security
    REQUIRE_HTTPS = os.getenv('REQUIRE_HTTPS', 'False').lower() == 'true'
    PRODUCTION_ACCESS_REQUIRES_2FA = os.getenv('PRODUCTION_ACCESS_REQUIRES_2FA', 'False').lower() == 'true'

    # Bookmarked Staging Environment
    STAGING_API_URL = os.getenv('STAGING_API_URL', 'https://staging-api.bookmarked.com')
    STAGING_API_USERNAME = os.getenv('STAGING_API_USERNAME')
    STAGING_API_PASSWORD = os.getenv('STAGING_API_PASSWORD')
    STAGING_DB_HOST = os.getenv('STAGING_DB_HOST')
    STAGING_DB_PORT = int(os.getenv('STAGING_DB_PORT', '5432'))
    STAGING_DB_NAME = os.getenv('STAGING_DB_NAME', 'bookmarked_staging')
    STAGING_DB_USER = os.getenv('STAGING_DB_USER')
    STAGING_DB_PASSWORD = os.getenv('STAGING_DB_PASSWORD')

    # Bookmarked Production Environment
    PRODUCTION_API_URL = os.getenv('PRODUCTION_API_URL', 'https://api.bookmarked.com')
    PRODUCTION_API_USERNAME = os.getenv('PRODUCTION_API_USERNAME')
    PRODUCTION_API_PASSWORD = os.getenv('PRODUCTION_API_PASSWORD')
    PRODUCTION_DB_HOST = os.getenv('PRODUCTION_DB_HOST')
    PRODUCTION_DB_PORT = int(os.getenv('PRODUCTION_DB_PORT', '5432'))
    PRODUCTION_DB_NAME = os.getenv('PRODUCTION_DB_NAME', 'bookmarked_production')
    PRODUCTION_DB_USER = os.getenv('PRODUCTION_DB_USER')
    PRODUCTION_DB_PASSWORD = os.getenv('PRODUCTION_DB_PASSWORD')

    # ClassLink Integration
    CLASSLINK_API_URL = os.getenv('CLASSLINK_API_URL', 'https://api.classlink.com/v2')
    CLASSLINK_API_KEY = os.getenv('CLASSLINK_API_KEY')
    CLASSLINK_OAUTH_CLIENT_ID = os.getenv('CLASSLINK_OAUTH_CLIENT_ID')
    CLASSLINK_OAUTH_CLIENT_SECRET = os.getenv('CLASSLINK_OAUTH_CLIENT_SECRET')

    # OneRoster Integration
    ONEROSTER_DEFAULT_VERSION = os.getenv('ONEROSTER_DEFAULT_VERSION', '1.2')

    # HubSpot Integration
    HUBSPOT_API_URL = os.getenv('HUBSPOT_API_URL', 'https://api.hubapi.com')
    HUBSPOT_CLIENT_ID = os.getenv('HUBSPOT_CLIENT_ID')
    HUBSPOT_CLIENT_SECRET = os.getenv('HUBSPOT_CLIENT_SECRET')
    HUBSPOT_REDIRECT_URI = os.getenv('HUBSPOT_REDIRECT_URI', 'http://localhost:6000/auth/hubspot/callback')

    # AWS Configuration
    AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_SECRETS_MANAGER_ENABLED = os.getenv('AWS_SECRETS_MANAGER_ENABLED', 'false').lower() == 'true'

    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/app.log')

    @classmethod
    def get_db_url(cls, environment: str) -> Optional[str]:
        """
        Generate database URL for the specified environment

        Args:
            environment: 'staging' or 'production'

        Returns:
            PostgreSQL connection URL or None if not configured
        """
        if environment == 'staging':
            if not all([cls.STAGING_DB_HOST, cls.STAGING_DB_USER, cls.STAGING_DB_PASSWORD]):
                return None
            return f"postgresql://{cls.STAGING_DB_USER}:{cls.STAGING_DB_PASSWORD}@{cls.STAGING_DB_HOST}:{cls.STAGING_DB_PORT}/{cls.STAGING_DB_NAME}"
        elif environment == 'production':
            if not all([cls.PRODUCTION_DB_HOST, cls.PRODUCTION_DB_USER, cls.PRODUCTION_DB_PASSWORD]):
                return None
            return f"postgresql://{cls.PRODUCTION_DB_USER}:{cls.PRODUCTION_DB_PASSWORD}@{cls.PRODUCTION_DB_HOST}:{cls.PRODUCTION_DB_PORT}/{cls.PRODUCTION_DB_NAME}"
        else:
            raise ValueError(f"Invalid environment: {environment}. Must be 'staging' or 'production'")

    @classmethod
    def is_configured(cls, service: str) -> bool:
        """
        Check if a service is properly configured

        Args:
            service: 'staging_db', 'production_db', 'classlink', 'hubspot', etc.

        Returns:
            True if all required credentials are present
        """
        if service == 'staging_db':
            return all([cls.STAGING_DB_HOST, cls.STAGING_DB_USER, cls.STAGING_DB_PASSWORD])
        elif service == 'production_db':
            return all([cls.PRODUCTION_DB_HOST, cls.PRODUCTION_DB_USER, cls.PRODUCTION_DB_PASSWORD])
        elif service == 'classlink':
            return bool(cls.CLASSLINK_API_KEY or (cls.CLASSLINK_OAUTH_CLIENT_ID and cls.CLASSLINK_OAUTH_CLIENT_SECRET))
        elif service == 'hubspot':
            return all([cls.HUBSPOT_CLIENT_ID, cls.HUBSPOT_CLIENT_SECRET])
        else:
            return False
