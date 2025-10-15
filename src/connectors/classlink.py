"""
ClassLink API Connector

Connector for ClassLink SIS integration platform.
Fetches OAuth credentials dynamically per district and accesses OneRoster data.
"""
import requests
from typing import Dict, Any, List, Optional
import structlog
import hmac
import hashlib
import base64
from urllib.parse import quote, urlparse
import time

logger = structlog.get_logger(__name__)


class OneRosterClient:
    """OAuth 1.0a client for OneRoster API"""

    def __init__(self, client_id: str, client_secret: str):
        """
        Initialize OneRoster client with OAuth credentials

        Args:
            client_id: OAuth 1.0a client ID
            client_secret: OAuth 1.0a client secret
        """
        self.client_id = client_id
        self.client_secret = client_secret

    def _generate_oauth_signature(self, method: str, url: str, params: Dict[str, str]) -> str:
        """
        Generate OAuth 1.0a HMAC-SHA256 signature

        Args:
            method: HTTP method (GET, POST, etc.)
            url: Full request URL
            params: Request parameters including OAuth params

        Returns:
            Base64-encoded signature
        """
        # Sort parameters
        sorted_params = sorted(params.items())

        # Create parameter string
        param_string = '&'.join([f'{quote(str(k), safe="")}={quote(str(v), safe="")}'
                                 for k, v in sorted_params])

        # Create signature base string
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
        signature_base = f"{method.upper()}&{quote(base_url, safe='')}&{quote(param_string, safe='')}"

        # Create signing key (consumer_secret&token_secret, but token_secret is empty for 2-legged OAuth)
        signing_key = f"{quote(self.client_secret, safe='')}&"

        # Generate HMAC-SHA256 signature
        signature = hmac.new(
            signing_key.encode('utf-8'),
            signature_base.encode('utf-8'),
            hashlib.sha256
        ).digest()

        return base64.b64encode(signature).decode('utf-8')

    def make_request(self, url: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict]:
        """
        Make authenticated request to OneRoster API

        Args:
            url: Full URL to request
            params: Query parameters

        Returns:
            JSON response or None
        """
        import random
        import string

        params = params or {}

        # Generate OAuth parameters (matching production: bookmarked-back/src/classlink/one-roster.ts)
        timestamp = str(int(time.time()))

        # Generate nonce: random alphanumeric string with length = timestamp length (usually 10)
        # See one-roster.ts line 28: generateNonce(timestamp.length)
        nonce_length = len(timestamp)
        nonce = ''.join(random.choices(string.ascii_letters + string.digits, k=nonce_length))

        oauth_params = {
            'oauth_consumer_key': self.client_id,
            'oauth_signature_method': 'HMAC-SHA256',
            'oauth_timestamp': timestamp,
            'oauth_nonce': nonce,
            # Note: Production does NOT include oauth_version
        }

        # Combine all parameters for signature
        all_params = {**params, **oauth_params}

        # Generate signature
        signature = self._generate_oauth_signature('GET', url, all_params)
        oauth_params['oauth_signature'] = signature

        # Build Authorization header
        auth_header = 'OAuth ' + ', '.join([f'{k}="{quote(str(v), safe="")}"'
                                            for k, v in sorted(oauth_params.items())])

        headers = {
            'Authorization': auth_header,
            'Content-Type': 'application/json'
        }

        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)

            if response.status_code == 200:
                return response.json()
            else:
                logger.error("OneRoster API request failed",
                           url=url,
                           status_code=response.status_code,
                           response=response.text[:200])
                return None

        except Exception as e:
            logger.error("OneRoster API request error", url=url, error=str(e))
            return None


class ClassLinkConnector:
    """Connector for ClassLink API"""

    def __init__(self, api_url: str = 'https://oneroster-proxy.classlink.io'):
        """
        Initialize ClassLink connector

        Args:
            api_url: Base URL for ClassLink API (default: production proxy used by bookmarked-back)
        """
        self.api_url = api_url.rstrip('/')
        self._district_cache = {}  # Cache district credentials

    def test_connection(self, api_key: str) -> Dict[str, Any]:
        """
        Test ClassLink API connection with provided API key

        Args:
            api_key: ClassLink API key (Bearer token)

        Returns:
            Dict with 'success' boolean and 'message' string
        """
        try:
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }

            # Test connection by getting district/application list
            # Note: Production uses /applications endpoint (see bookmarked-back/.api/apis/classlink/index.ts line 91)
            response = requests.get(
                f'{self.api_url}/applications',
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                applications = data.get('applications', [])

                logger.info("ClassLink connection test successful",
                           district_count=len(applications))

                return {
                    'success': True,
                    'message': f'Connected to ClassLink successfully - {len(applications)} districts available',
                    'details': {
                        'district_count': len(applications),
                        'districts': [{'id': app.get('id'), 'name': app.get('name')}
                                     for app in applications[:5]]  # First 5 districts
                    }
                }
            else:
                logger.error("ClassLink connection test failed",
                            status_code=response.status_code,
                            response=response.text[:200])

                return {
                    'success': False,
                    'message': f'Connection failed: {response.status_code} - {response.text[:100]}',
                    'details': None
                }

        except requests.exceptions.Timeout:
            logger.error("ClassLink connection timeout")
            return {
                'success': False,
                'message': 'Connection timeout - ClassLink API did not respond',
                'details': None
            }
        except requests.exceptions.RequestException as e:
            logger.error("ClassLink connection request failed", error=str(e))
            return {
                'success': False,
                'message': f'Connection failed: {str(e)}',
                'details': None
            }
        except Exception as e:
            logger.error("Unexpected error testing ClassLink connection", error=str(e))
            return {
                'success': False,
                'message': f'Unexpected error: {str(e)}',
                'details': None
            }

    def get_district_credentials(self, bearer_token: str, oneroster_app_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch OAuth credentials for a specific district

        This calls the ClassLink API to get the OneRoster endpoint and OAuth credentials
        for a specific district, just like the production backend does.

        Args:
            bearer_token: ClassLink Bearer token
            oneroster_app_id: OneRoster application ID (from ClasslinkApplication.oneroster_application_id)
                             This is the URL-encoded ID like "XHkpmX1KunU%3D"

        Returns:
            Dict with endpoint_url, client_id, client_secret or None
        """
        # Check cache first
        cache_key = f"{oneroster_app_id}"
        if cache_key in self._district_cache:
            logger.debug("Using cached credentials", oneroster_app_id=oneroster_app_id)
            return self._district_cache[cache_key]

        try:
            headers = {
                'Authorization': f'Bearer {bearer_token}',
                'Content-Type': 'application/json'
            }

            # Get district server details
            response = requests.get(
                f'{self.api_url}/applications/{oneroster_app_id}/server',
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                server_data = data.get('server', {})

                credentials = {
                    'endpoint_url': server_data.get('endpoint_url'),
                    'client_id': server_data.get('client_id'),
                    'client_secret': server_data.get('client_secret')
                }

                # Cache the credentials
                self._district_cache[cache_key] = credentials

                logger.info("Retrieved district credentials",
                           oneroster_app_id=oneroster_app_id,
                           endpoint_url=credentials['endpoint_url'])

                return credentials
            else:
                logger.error("Failed to get district credentials",
                            oneroster_app_id=oneroster_app_id,
                            status_code=response.status_code,
                            response=response.text[:200])
                return None

        except Exception as e:
            logger.error("Error getting district credentials",
                        oneroster_app_id=oneroster_app_id,
                        error=str(e))
            return None

    def get_users(self, bearer_token: str, oneroster_app_id: str,
                  limit: int = 100, offset: int = 0, role: Optional[str] = None) -> List[Dict]:
        """
        Get users from ClassLink for a specific district

        Args:
            bearer_token: ClassLink Bearer token
            oneroster_app_id: OneRoster application ID
            limit: Maximum number of results (default 100)
            offset: Offset for pagination (default 0)
            role: Optional filter by role (student, parent, guardian, teacher, etc.)

        Returns:
            List of user dictionaries
        """
        # Get district credentials
        creds = self.get_district_credentials(bearer_token, oneroster_app_id)
        if not creds:
            logger.error("Cannot get users - no credentials available")
            return []

        # Create OneRoster client
        client = OneRosterClient(creds['client_id'], creds['client_secret'])

        # Fetch users
        url = f"{creds['endpoint_url']}/ims/oneroster/v1p1/users"
        params = {'limit': limit, 'offset': offset, 'orderBy': 'asc'}

        data = client.make_request(url, params)
        if data:
            users = data.get('users', [])

            # Filter by role if specified
            if role:
                users = [u for u in users if u.get('role') == role]

            logger.info("Retrieved users", count=len(users), role=role, oneroster_app_id=oneroster_app_id)
            return users

        return []

    def get_students(self, bearer_token: str, oneroster_app_id: str,
                    limit: int = 100, offset: int = 0) -> List[Dict]:
        """
        Get students from ClassLink for a specific district

        Args:
            bearer_token: ClassLink Bearer token
            oneroster_app_id: OneRoster application ID
            limit: Maximum number of results (default 100)
            offset: Offset for pagination (default 0)

        Returns:
            List of student dictionaries
        """
        return self.get_users(bearer_token, oneroster_app_id, limit, offset, role='student')

    def get_schools(self, bearer_token: str, oneroster_app_id: str,
                   limit: int = 100, offset: int = 0) -> List[Dict]:
        """
        Get schools/organizations from ClassLink for a specific district

        Args:
            bearer_token: ClassLink Bearer token
            oneroster_app_id: OneRoster application ID
            limit: Maximum number of results (default 100)
            offset: Offset for pagination (default 0)

        Returns:
            List of organization dictionaries
        """
        # Get district credentials
        creds = self.get_district_credentials(bearer_token, oneroster_app_id)
        if not creds:
            logger.error("Cannot get schools - no credentials available")
            return []

        # Create OneRoster client
        client = OneRosterClient(creds['client_id'], creds['client_secret'])

        # Fetch organizations
        url = f"{creds['endpoint_url']}/ims/oneroster/v1p1/orgs"
        params = {'limit': limit, 'offset': offset, 'orderBy': 'asc'}

        data = client.make_request(url, params)
        if data:
            orgs = data.get('orgs', [])
            logger.info("Retrieved schools", count=len(orgs), oneroster_app_id=oneroster_app_id)
            return orgs

        return []

    def get_classes(self, bearer_token: str, oneroster_app_id: str,
                   limit: int = 100, offset: int = 0) -> List[Dict]:
        """
        Get classes from ClassLink for a specific district

        Args:
            bearer_token: ClassLink Bearer token
            oneroster_app_id: OneRoster application ID
            limit: Maximum number of results (default 100)
            offset: Offset for pagination (default 0)

        Returns:
            List of class dictionaries
        """
        # Get district credentials
        creds = self.get_district_credentials(bearer_token, oneroster_app_id)
        if not creds:
            logger.error("Cannot get classes - no credentials available")
            return []

        # Create OneRoster client
        client = OneRosterClient(creds['client_id'], creds['client_secret'])

        # Fetch classes
        url = f"{creds['endpoint_url']}/ims/oneroster/v1p1/classes"
        params = {'limit': limit, 'offset': offset, 'orderBy': 'asc'}

        data = client.make_request(url, params)
        if data:
            classes = data.get('classes', [])
            logger.info("Retrieved classes", count=len(classes), oneroster_app_id=oneroster_app_id)
            return classes

        return []

    def validate_district_data(self, bearer_token: str, oneroster_app_id: str) -> Dict[str, Any]:
        """
        Validate ClassLink data quality for a specific district

        Args:
            bearer_token: ClassLink Bearer token
            oneroster_app_id: OneRoster application ID

        Returns:
            Dict with validation results
        """
        logger.info("Starting ClassLink data validation", oneroster_app_id=oneroster_app_id)

        validation_results = {
            'success': True,
            'errors': [],
            'warnings': [],
            'stats': {},
            'oneroster_app_id': oneroster_app_id
        }

        try:
            # Get credentials first
            creds = self.get_district_credentials(bearer_token, oneroster_app_id)
            if not creds:
                validation_results['success'] = False
                validation_results['errors'].append('Failed to get district credentials')
                return validation_results

            validation_results['stats']['endpoint_url'] = creds['endpoint_url']

            # Check schools
            schools = self.get_schools(bearer_token, oneroster_app_id, limit=100)
            validation_results['stats']['schools_count'] = len(schools)

            if len(schools) == 0:
                validation_results['warnings'].append('No schools found for this district')

            # Check students
            students = self.get_students(bearer_token, oneroster_app_id, limit=100)
            validation_results['stats']['students_count'] = len(students)

            if len(students) == 0:
                validation_results['warnings'].append('No students found for this district')

            # Validate student data quality
            students_missing_email = 0
            students_missing_name = 0

            for student in students[:50]:  # Sample first 50
                if not student.get('email'):
                    students_missing_email += 1
                if not student.get('givenName') or not student.get('familyName'):
                    students_missing_name += 1

            if students_missing_email > 0:
                validation_results['warnings'].append(
                    f'{students_missing_email} students missing email addresses (sample of 50)'
                )

            if students_missing_name > 0:
                validation_results['warnings'].append(
                    f'{students_missing_name} students missing name fields (sample of 50)'
                )

            # Check classes
            classes = self.get_classes(bearer_token, oneroster_app_id, limit=100)
            validation_results['stats']['classes_count'] = len(classes)

            if len(classes) == 0:
                validation_results['warnings'].append('No classes found for this district')

            logger.info("ClassLink data validation completed",
                       oneroster_app_id=oneroster_app_id,
                       success=validation_results['success'],
                       errors=len(validation_results['errors']),
                       warnings=len(validation_results['warnings']))

        except Exception as e:
            logger.error("Error during ClassLink data validation",
                        oneroster_app_id=oneroster_app_id,
                        error=str(e))
            validation_results['success'] = False
            validation_results['errors'].append(f'Validation failed: {str(e)}')

        return validation_results
