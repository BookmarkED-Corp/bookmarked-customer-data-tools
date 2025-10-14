"""
HubSpot OAuth2 Authentication Routes

Handles OAuth2 flow for HubSpot integration.
"""
from flask import Blueprint, request, redirect, url_for, jsonify, session, render_template_string
import requests
import os
from urllib.parse import urlencode
import structlog

logger = structlog.get_logger(__name__)

hubspot_auth_bp = Blueprint('hubspot_auth', __name__)


def get_oauth_config():
    """Get HubSpot OAuth configuration from environment"""
    return {
        'client_id': os.getenv('HUBSPOT_CLIENT_ID'),
        'client_secret': os.getenv('HUBSPOT_CLIENT_SECRET'),
        'redirect_uri': os.getenv('HUBSPOT_REDIRECT_URI', 'http://localhost:6001/auth/hubspot/callback'),
        'auth_url': 'https://app.hubspot.com/oauth/authorize',
        'token_url': 'https://api.hubapi.com/oauth/v1/token'
    }


@hubspot_auth_bp.route('/auth/hubspot/start')
def start_oauth():
    """
    Start HubSpot OAuth flow
    Redirects user to HubSpot login
    """
    config = get_oauth_config()

    if not config['client_id']:
        return jsonify({
            'error': 'HubSpot OAuth not configured',
            'message': 'Please set HUBSPOT_CLIENT_ID and HUBSPOT_CLIENT_SECRET in .env'
        }), 400

    # Build authorization URL
    params = {
        'client_id': config['client_id'],
        'redirect_uri': config['redirect_uri'],
        'scope': 'tickets crm.objects.contacts.read crm.objects.contacts.write'
    }

    auth_url = f"{config['auth_url']}?{urlencode(params)}"

    logger.info("Starting HubSpot OAuth flow", redirect_uri=config['redirect_uri'])

    return redirect(auth_url)


@hubspot_auth_bp.route('/auth/hubspot/callback')
def oauth_callback():
    """
    Handle OAuth callback from HubSpot
    Exchanges authorization code for access token
    """
    config = get_oauth_config()

    # Check for error
    error = request.args.get('error')
    if error:
        error_description = request.args.get('error_description', 'Unknown error')
        logger.error("HubSpot OAuth error", error=error, description=error_description)

        return render_template_string("""
            <!DOCTYPE html>
            <html>
            <head>
                <title>HubSpot Authentication Failed</title>
                <style>
                    body {
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                        margin: 0;
                        background: #f8f9fa;
                    }
                    .container {
                        background: white;
                        padding: 40px;
                        border-radius: 8px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                        text-align: center;
                        max-width: 500px;
                    }
                    .error {
                        color: #dc3545;
                        font-size: 48px;
                        margin-bottom: 20px;
                    }
                    h1 {
                        color: #333;
                        margin-bottom: 10px;
                    }
                    p {
                        color: #666;
                        margin-bottom: 30px;
                    }
                    button {
                        background: #ff6227;
                        color: white;
                        border: none;
                        padding: 12px 24px;
                        border-radius: 4px;
                        font-size: 16px;
                        cursor: pointer;
                    }
                    button:hover {
                        background: #e5551f;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="error">✗</div>
                    <h1>Authentication Failed</h1>
                    <p>{{ error }}: {{ error_description }}</p>
                    <button onclick="window.close()">Close Window</button>
                </div>
            </body>
            </html>
        """, error=error, error_description=error_description)

    # Get authorization code
    code = request.args.get('code')
    if not code:
        return jsonify({'error': 'No authorization code received'}), 400

    # Exchange code for access token
    try:
        token_data = {
            'grant_type': 'authorization_code',
            'client_id': config['client_id'],
            'client_secret': config['client_secret'],
            'redirect_uri': config['redirect_uri'],
            'code': code
        }

        response = requests.post(
            config['token_url'],
            data=token_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=10
        )

        if response.status_code == 200:
            token_info = response.json()
            access_token = token_info['access_token']
            refresh_token = token_info.get('refresh_token')
            expires_in = token_info.get('expires_in')

            # Store tokens in session (in production, store in database)
            session['hubspot_access_token'] = access_token
            session['hubspot_refresh_token'] = refresh_token

            logger.info("HubSpot OAuth successful",
                       expires_in=expires_in,
                       has_refresh_token=bool(refresh_token))

            # Return success page that closes itself
            return render_template_string("""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>HubSpot Authentication Successful</title>
                    <style>
                        body {
                            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            height: 100vh;
                            margin: 0;
                            background: #f8f9fa;
                        }
                        .container {
                            background: white;
                            padding: 40px;
                            border-radius: 8px;
                            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                            text-align: center;
                            max-width: 500px;
                        }
                        .success {
                            color: #15b79e;
                            font-size: 48px;
                            margin-bottom: 20px;
                        }
                        h1 {
                            color: #333;
                            margin-bottom: 10px;
                        }
                        p {
                            color: #666;
                            margin-bottom: 30px;
                        }
                        .spinner {
                            border: 3px solid #f3f3f3;
                            border-top: 3px solid #15b79e;
                            border-radius: 50%;
                            width: 40px;
                            height: 40px;
                            animation: spin 1s linear infinite;
                            margin: 20px auto;
                        }
                        @keyframes spin {
                            0% { transform: rotate(0deg); }
                            100% { transform: rotate(360deg); }
                        }
                    </style>
                    <script>
                        // Send token to parent window
                        if (window.opener) {
                            window.opener.postMessage({
                                type: 'hubspot_auth_success',
                                access_token: '{{ access_token }}',
                                refresh_token: '{{ refresh_token }}'
                            }, window.location.origin);
                        }

                        // Close window after 2 seconds
                        setTimeout(function() {
                            window.close();
                        }, 2000);
                    </script>
                </head>
                <body>
                    <div class="container">
                        <div class="success">✓</div>
                        <h1>Authentication Successful!</h1>
                        <p>HubSpot connected successfully.</p>
                        <div class="spinner"></div>
                        <p style="font-size: 14px; color: #999;">This window will close automatically...</p>
                    </div>
                </body>
                </html>
            """, access_token=access_token, refresh_token=refresh_token or '')

        else:
            logger.error("Token exchange failed",
                        status_code=response.status_code,
                        response=response.text[:200])

            return jsonify({
                'error': 'Token exchange failed',
                'details': response.text
            }), 500

    except Exception as e:
        logger.error("OAuth callback error", error=str(e))
        return jsonify({
            'error': 'Authentication failed',
            'details': str(e)
        }), 500


@hubspot_auth_bp.route('/api/hubspot/status')
def hubspot_status():
    """Check if HubSpot is authenticated"""
    access_token = session.get('hubspot_access_token')

    if access_token:
        # Test token validity
        try:
            response = requests.get(
                'https://api.hubapi.com/account-info/v3/details',
                headers={'Authorization': f'Bearer {access_token}'},
                timeout=5
            )

            if response.status_code == 200:
                account_data = response.json()
                return jsonify({
                    'authenticated': True,
                    'portal_id': account_data.get('portalId'),
                    'time_zone': account_data.get('timeZone')
                })
        except:
            pass

    return jsonify({'authenticated': False})
