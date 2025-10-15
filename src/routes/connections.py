"""
Connection Setup Routes

Routes for testing and saving database and API connections.
"""
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from src.connectors.bookmarked_db import BookmarkedDBConnector
from src.connectors.bookmarked_api import BookmarkedAPIConnector
from src.connectors.hubspot import HubSpotConnector
from src.connectors.clickup import ClickUpConnector
from src.connectors.classlink import ClassLinkConnector
from src.utils.connections import ConnectionsConfig
import structlog

logger = structlog.get_logger(__name__)

connections_bp = Blueprint('connections', __name__)


@connections_bp.route('/connections/setup')
def setup():
    """Display connections setup page"""
    # Load existing connections if any
    config_manager = ConnectionsConfig()
    existing_connections = config_manager.load_connections() or {}

    return render_template('connections/setup.html',
                          existing_connections=existing_connections)


@connections_bp.route('/api/connections/test/staging', methods=['POST'])
def test_staging():
    """Test staging database connection"""
    data = request.json

    connector = BookmarkedDBConnector(environment='staging')
    result = connector.test_connection(
        host=data.get('host'),
        port=int(data.get('port', 5432)),
        database=data.get('database'),
        user=data.get('user'),
        password=data.get('password')
    )

    return jsonify(result)


@connections_bp.route('/api/connections/test/production', methods=['POST'])
def test_production():
    """Test production database connection"""
    data = request.json

    connector = BookmarkedDBConnector(environment='production')
    result = connector.test_connection(
        host=data.get('host'),
        port=int(data.get('port', 5432)),
        database=data.get('database'),
        user=data.get('user'),
        password=data.get('password')
    )

    return jsonify(result)


@connections_bp.route('/api/connections/test/staging-api', methods=['POST'])
def test_staging_api():
    """Test staging API connection"""
    data = request.json

    connector = BookmarkedAPIConnector(environment='staging')
    result = connector.test_connection(
        base_url=data.get('base_url'),
        username=data.get('username'),
        password=data.get('password')
    )

    return jsonify(result)


@connections_bp.route('/api/connections/test/production-api', methods=['POST'])
def test_production_api():
    """Test production API connection"""
    data = request.json

    connector = BookmarkedAPIConnector(environment='production')
    result = connector.test_connection(
        base_url=data.get('base_url'),
        username=data.get('username'),
        password=data.get('password')
    )

    return jsonify(result)


@connections_bp.route('/api/connections/test/hubspot', methods=['POST'])
def test_hubspot():
    """Test HubSpot API connection"""
    data = request.json

    connector = HubSpotConnector()
    result = connector.test_connection(
        access_token=data.get('access_token')
    )

    return jsonify(result)


@connections_bp.route('/api/connections/test/clickup', methods=['POST'])
def test_clickup():
    """Test ClickUp API connection"""
    data = request.json

    connector = ClickUpConnector()
    result = connector.test_connection(
        api_key=data.get('api_key')
    )

    return jsonify(result)


@connections_bp.route('/api/connections/test/classlink', methods=['POST'])
def test_classlink():
    """Test ClassLink API connection"""
    data = request.json

    connector = ClassLinkConnector()
    result = connector.test_connection(
        api_key=data.get('api_key')
    )

    return jsonify(result)


@connections_bp.route('/api/connections/validate/classlink', methods=['POST'])
def validate_classlink():
    """Validate ClassLink data quality"""
    data = request.json

    connector = ClassLinkConnector()
    result = connector.validate_data_quality(
        api_key=data.get('api_key')
    )

    return jsonify(result)


@connections_bp.route('/api/connections/save', methods=['POST'])
def save_connections():
    """Save all connection configurations"""
    data = request.json

    config_manager = ConnectionsConfig()

    connections = {}

    # Staging (with nested db and api)
    if data.get('staging'):
        staging = data['staging']
        connections['staging'] = {
            'db': {
                'host': staging.get('db', {}).get('host'),
                'port': int(staging.get('db', {}).get('port', 5432)),
                'database': staging.get('db', {}).get('database'),
                'user': staging.get('db', {}).get('user'),
                'password': staging.get('db', {}).get('password')
            },
            'api': {
                'base_url': staging.get('api', {}).get('base_url'),
                'username': staging.get('api', {}).get('username'),
                'password': staging.get('api', {}).get('password')
            },
            'enabled': staging.get('enabled', True)
        }

    # Production (with nested db and api)
    if data.get('production'):
        production = data['production']
        connections['production'] = {
            'db': {
                'host': production.get('db', {}).get('host'),
                'port': int(production.get('db', {}).get('port', 5432)),
                'database': production.get('db', {}).get('database'),
                'user': production.get('db', {}).get('user'),
                'password': production.get('db', {}).get('password')
            },
            'api': {
                'base_url': production.get('api', {}).get('base_url'),
                'username': production.get('api', {}).get('username'),
                'password': production.get('api', {}).get('password')
            },
            'enabled': production.get('enabled', True)
        }

    # HubSpot
    if data.get('hubspot'):
        connections['hubspot'] = {
            'access_token': data['hubspot'].get('access_token'),
            'enabled': data['hubspot'].get('enabled', True)
        }

    # ClickUp
    if data.get('clickup'):
        connections['clickup'] = {
            'api_key': data['clickup'].get('api_key'),
            'enabled': data['clickup'].get('enabled', True)
        }

    # ClassLink
    if data.get('classlink'):
        connections['classlink'] = {
            'api_key': data['classlink'].get('api_key'),
            'enabled': data['classlink'].get('enabled', True)
        }

    success = config_manager.save_connections(connections)

    if success:
        logger.info("Connections saved successfully")
        return jsonify({
            'success': True,
            'message': 'Connections saved successfully'
        })
    else:
        logger.error("Failed to save connections")
        return jsonify({
            'success': False,
            'message': 'Failed to save connections'
        }), 500


@connections_bp.route('/api/connections/load', methods=['GET'])
def load_connections():
    """Load saved connection configurations"""
    config_manager = ConnectionsConfig()
    connections = config_manager.load_connections()

    if connections:
        # Mask passwords in response
        safe_connections = {}
        for key, config in connections.items():
            import copy
            safe_config = copy.deepcopy(config)

            # Handle nested structure (staging/production with db and api)
            if key in ['staging', 'production']:
                if 'db' in safe_config and 'password' in safe_config['db']:
                    safe_config['db']['password'] = '****' if safe_config['db']['password'] else ''
                if 'api' in safe_config and 'password' in safe_config['api']:
                    safe_config['api']['password'] = '****' if safe_config['api']['password'] else ''

            # Handle flat structure (backward compatibility)
            if 'password' in safe_config:
                safe_config['password'] = '****' if safe_config['password'] else ''
            if 'access_token' in safe_config:
                safe_config['access_token'] = '****' if safe_config['access_token'] else ''
            if 'api_key' in safe_config:
                safe_config['api_key'] = '****' if safe_config['api_key'] else ''
            safe_connections[key] = safe_config

        return jsonify({
            'success': True,
            'connections': safe_connections
        })
    else:
        return jsonify({
            'success': False,
            'message': 'No saved connections found'
        })


@connections_bp.route('/api/connections/defaults', methods=['GET'])
def load_defaults():
    """Load default connection configurations from machine-specific config"""
    config_manager = ConnectionsConfig()
    defaults = config_manager.load_defaults()

    if defaults:
        # Return defaults as-is (they will be used to pre-fill forms)
        return jsonify({
            'success': True,
            'defaults': defaults
        })
    else:
        return jsonify({
            'success': False,
            'message': 'No defaults file found'
        })
