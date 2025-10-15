"""
Secrets Management

Load secrets from secrets.yml file (similar to k8s secrets pattern)
"""
import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import structlog

logger = structlog.get_logger(__name__)


class SecretsManager:
    """Manage secrets from secrets.yml file"""

    def __init__(self, secrets_file: str = 'secrets.yml'):
        """
        Initialize secrets manager

        Args:
            secrets_file: Path to secrets.yml file
        """
        self.secrets_file = Path(secrets_file)
        self._secrets: Optional[Dict[str, Any]] = None
        self._load_secrets()

    def _load_secrets(self):
        """Load secrets from YAML file"""
        if not self.secrets_file.exists():
            logger.warning("Secrets file not found",
                         secrets_file=str(self.secrets_file))
            self._secrets = {}
            return

        try:
            with open(self.secrets_file, 'r') as f:
                self._secrets = yaml.safe_load(f) or {}

            logger.info("Secrets loaded successfully",
                       num_secrets=len(self._secrets),
                       secrets_file=str(self.secrets_file))

        except Exception as e:
            logger.error("Failed to load secrets",
                        error=str(e),
                        secrets_file=str(self.secrets_file))
            self._secrets = {}

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a secret value

        Args:
            key: Secret key
            default: Default value if key not found

        Returns:
            Secret value or default
        """
        # Check environment variable first (highest priority)
        env_value = os.getenv(key)
        if env_value is not None:
            return env_value

        # Check secrets file
        if self._secrets and key in self._secrets:
            return self._secrets[key]

        return default

    def get_int(self, key: str, default: int = 0) -> int:
        """Get secret as integer"""
        value = self.get(key, default)
        try:
            return int(value)
        except (ValueError, TypeError):
            return default

    def get_bool(self, key: str, default: bool = False) -> bool:
        """Get secret as boolean"""
        value = self.get(key, default)
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'enabled')
        return default

    def get_all(self) -> Dict[str, Any]:
        """Get all secrets"""
        return self._secrets.copy() if self._secrets else {}

    def reload(self):
        """Reload secrets from file"""
        self._load_secrets()


# Global secrets manager instance
_secrets_manager: Optional[SecretsManager] = None


def get_secrets_manager() -> SecretsManager:
    """Get global secrets manager instance"""
    global _secrets_manager
    if _secrets_manager is None:
        _secrets_manager = SecretsManager()
    return _secrets_manager


def get_secret(key: str, default: Any = None) -> Any:
    """Convenience function to get a secret"""
    return get_secrets_manager().get(key, default)


def get_secret_int(key: str, default: int = 0) -> int:
    """Convenience function to get a secret as integer"""
    return get_secrets_manager().get_int(key, default)


def get_secret_bool(key: str, default: bool = False) -> bool:
    """Convenience function to get a secret as boolean"""
    return get_secrets_manager().get_bool(key, default)
