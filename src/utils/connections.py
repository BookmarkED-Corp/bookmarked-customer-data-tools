"""
Connection Configuration Management

Handles saving and loading connection configurations.
"""
import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
import structlog

logger = structlog.get_logger(__name__)


class ConnectionsConfig:
    """Manages connection configurations with encryption"""

    def __init__(self, config_dir: str = 'config'):
        """
        Initialize connections config manager

        Args:
            config_dir: Directory to store config files
        """
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / 'connections.config'
        self.key_file = self.config_dir / '.connection_key'
        self.defaults_file = self.config_dir / 'defaults.json'

        # Load or generate encryption key
        self._encryption_key = self._load_or_generate_key()

    def _load_or_generate_key(self) -> bytes:
        """Load existing encryption key or generate new one"""
        if self.key_file.exists():
            with open(self.key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
            # Set restrictive permissions
            os.chmod(self.key_file, 0o600)
            logger.info("Generated new encryption key", key_file=str(self.key_file))
            return key

    def _encrypt(self, data: str) -> str:
        """Encrypt string data"""
        f = Fernet(self._encryption_key)
        return f.encrypt(data.encode()).decode()

    def _decrypt(self, encrypted_data: str) -> str:
        """Decrypt string data"""
        f = Fernet(self._encryption_key)
        return f.decrypt(encrypted_data.encode()).decode()

    def save_connections(self, connections: Dict[str, Any]) -> bool:
        """
        Save connection configurations

        Args:
            connections: Dictionary of connection configs
                {
                    'staging': {...},
                    'production': {...},
                    'hubspot': {...}
                }

        Returns:
            True if successful
        """
        try:
            # Encrypt sensitive data
            encrypted_connections = {}
            for key, config in connections.items():
                encrypted_config = {}
                for field, value in config.items():
                    # Encrypt passwords, tokens, and api keys
                    if 'password' in field.lower() or 'token' in field.lower() or 'api_key' in field.lower():
                        encrypted_config[field] = self._encrypt(str(value))
                        encrypted_config[f'{field}_encrypted'] = True
                    else:
                        encrypted_config[field] = value
                encrypted_connections[key] = encrypted_config

            # Save to file
            with open(self.config_file, 'w') as f:
                json.dump(encrypted_connections, f, indent=2)

            # Set restrictive permissions
            os.chmod(self.config_file, 0o600)

            logger.info("Connections saved",
                       config_file=str(self.config_file),
                       num_connections=len(connections))
            return True

        except Exception as e:
            logger.error("Failed to save connections",
                        error=str(e))
            return False

    def load_connections(self) -> Optional[Dict[str, Any]]:
        """
        Load connection configurations

        Returns:
            Dictionary of connection configs or None if not found
        """
        if not self.config_file.exists():
            logger.warning("No connections config file found",
                         config_file=str(self.config_file))
            return None

        try:
            with open(self.config_file, 'r') as f:
                encrypted_connections = json.load(f)

            # Decrypt sensitive data
            connections = {}
            for key, encrypted_config in encrypted_connections.items():
                config = {}
                for field, value in encrypted_config.items():
                    # Skip the _encrypted flags
                    if field.endswith('_encrypted'):
                        continue

                    # Decrypt if marked as encrypted
                    if encrypted_config.get(f'{field}_encrypted'):
                        config[field] = self._decrypt(value)
                    else:
                        config[field] = value
                connections[key] = config

            logger.info("Connections loaded",
                       num_connections=len(connections))
            return connections

        except Exception as e:
            logger.error("Failed to load connections",
                        error=str(e))
            return None

    def delete_connections(self) -> bool:
        """
        Delete saved connections

        Returns:
            True if successful
        """
        try:
            if self.config_file.exists():
                self.config_file.unlink()
                logger.info("Connections deleted")
            return True
        except Exception as e:
            logger.error("Failed to delete connections",
                        error=str(e))
            return False

    def get_connection(self, connection_type: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific connection config

        Args:
            connection_type: 'staging', 'production', or 'hubspot'

        Returns:
            Connection config or None
        """
        connections = self.load_connections()
        if connections:
            return connections.get(connection_type)
        return None

    def load_defaults(self) -> Optional[Dict[str, Any]]:
        """
        Load default connection values from defaults.json

        Returns:
            Dictionary of default connection configs or None if not found
        """
        if not self.defaults_file.exists():
            logger.info("No defaults file found",
                       defaults_file=str(self.defaults_file))
            return None

        try:
            with open(self.defaults_file, 'r') as f:
                defaults = json.load(f)

            logger.info("Defaults loaded",
                       num_defaults=len(defaults))
            return defaults

        except Exception as e:
            logger.error("Failed to load defaults",
                        error=str(e))
            return None
