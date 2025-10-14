"""
Connection Setup Routes

Routes for testing and saving database and API connections.
"""
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from src.connectors.bookmarked_db import BookmarkedDBConnector
from src.connectors.hubspot import HubSpotConnector
from src.connectors.clickup import ClickUpConnector
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


@connections_bp.route('/api/connections/save', methods=['POST'])
def save_connections():
    """Save all connection configurations"""
    data = request.json

    config_manager = ConnectionsConfig()

    connections = {}

    # Staging database
    if data.get('staging'):
        connections['staging'] = {
            'host': data['staging'].get('host'),
            'port': int(data['staging'].get('port', 5432)),
            'database': data['staging'].get('database'),
            'user': data['staging'].get('user'),
            'password': data['staging'].get('password'),
            'enabled': data['staging'].get('enabled', True)
        }

    # Production database
    if data.get('production'):
        connections['production'] = {
            'host': data['production'].get('host'),
            'port': int(data['production'].get('port', 5432)),
            'database': data['production'].get('database'),
            'user': data['production'].get('user'),
            'password': data['production'].get('password'),
            'enabled': data['production'].get('enabled', True)
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
            safe_config = config.copy()
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
