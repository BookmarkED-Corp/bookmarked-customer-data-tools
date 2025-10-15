"""
Bookmarked REST API Connector

REST API client for Bookmarked backend API supporting both staging and production environments.
Uses JWT Bearer token authentication.
"""
import requests
from typing import Optional, Dict, Any, List
import structlog

logger = structlog.get_logger(__name__)


class BookmarkedAPIConnector:
    """REST API client for Bookmarked backend"""

    def __init__(self, environment: str = 'staging'):
        """
        Initialize API connector

        Args:
            environment: 'staging' or 'production'
        """
        self.environment = environment
        self.base_url = None
        self.jwt_token = None
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': '*/*',
            'x-locale': 'en'
        })

    def _login(self, base_url: str, username: str, password: str) -> Optional[str]:
        """
        Login to get JWT token

        Args:
            base_url: API base URL
            username: Login username/email
            password: Login password

        Returns:
            JWT token string or None if login failed
        """
        try:
            login_url = f"{base_url}/auth/"

            logger.info("Attempting login",
                       environment=self.environment,
                       login_url=login_url,
                       username=username)

            response = self.session.post(
                login_url,
                json={
                    'email': username,
                    'password': password
                },
                timeout=10
            )

            logger.info("Login response received",
                       environment=self.environment,
                       status_code=response.status_code)

            if response.status_code == 200:
                data = response.json()
                token = data.get('token') or data.get('access_token') or data.get('accessToken')

                if token:
                    logger.info("Login successful, JWT token obtained",
                               environment=self.environment)
                    return token
                else:
                    logger.warning("Login response missing token",
                                  environment=self.environment,
                                  response=data)
                    return None
            else:
                logger.warning("Login failed",
                              environment=self.environment,
                              status_code=response.status_code,
                              url=login_url,
                              response=response.text[:500])
                return None

        except Exception as e:
            logger.error("Login error",
                        environment=self.environment,
                        error=str(e))
            return None

    def test_connection(self, base_url: str, username: str, password: str) -> Dict[str, Any]:
        """
        Test API connection with provided credentials

        Args:
            base_url: API base URL (e.g., https://stg.api.bookmarked.com)
            username: API username/email
            password: API password

        Returns:
            Dict with 'success' boolean and 'message' string
        """
        try:
            # Step 1: Login to get JWT token
            token = self._login(base_url, username, password)

            if not token:
                return {
                    'success': False,
                    'message': 'Login failed - could not obtain JWT token',
                    'details': {
                        'login_url': f"{base_url}/auth/login"
                    }
                }

            # Step 2: Test with a simple authenticated endpoint
            # Use a lightweight endpoint that should exist
            test_url = f"{base_url}/auth/health-check"

            headers = {
                'Authorization': f'Bearer {token}',
                'x-locale': 'en'
            }

            response = self.session.get(
                test_url,
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                logger.info("API connection test successful",
                           environment=self.environment,
                           url=base_url)

                return {
                    'success': True,
                    'message': 'Connection successful',
                    'details': {
                        'url': base_url,
                        'status_code': response.status_code,
                        'response_time': response.elapsed.total_seconds()
                    }
                }
            else:
                logger.warning("API connection test failed with non-200 status",
                              environment=self.environment,
                              status_code=response.status_code)

                return {
                    'success': False,
                    'message': f'Connection failed: HTTP {response.status_code}',
                    'details': {
                        'status_code': response.status_code,
                        'response': response.text[:200]
                    }
                }

        except requests.exceptions.ConnectionError as e:
            logger.error("API connection failed - connection error",
                        environment=self.environment,
                        error=str(e))
            return {
                'success': False,
                'message': f'Connection error: {str(e)}',
                'details': None
            }
        except requests.exceptions.Timeout:
            logger.error("API connection failed - timeout",
                        environment=self.environment)
            return {
                'success': False,
                'message': 'Connection timeout after 10 seconds',
                'details': None
            }
        except Exception as e:
            logger.error("Unexpected error testing API connection",
                        environment=self.environment,
                        error=str(e))
            return {
                'success': False,
                'message': f'Unexpected error: {str(e)}',
                'details': None
            }

    def connect(self, base_url: str, username: str, password: str) -> bool:
        """
        Establish API connection with JWT authentication

        Args:
            base_url: API base URL
            username: API username/email
            password: API password

        Returns:
            True if connection successful
        """
        try:
            self.base_url = base_url.rstrip('/')

            # Login to get JWT token
            self.jwt_token = self._login(self.base_url, username, password)

            if self.jwt_token:
                logger.info("API connection established",
                           environment=self.environment,
                           url=self.base_url)
                return True
            else:
                logger.error("Failed to establish API connection - login failed",
                            environment=self.environment)
                return False

        except Exception as e:
            logger.error("Failed to establish API connection",
                        environment=self.environment,
                        error=str(e))
            return False

    def get_districts(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get list of districts from API

        Args:
            limit: Maximum number of results
            offset: Offset for pagination

        Returns:
            List of district records
        """
        if not self.base_url or not self.jwt_token:
            raise RuntimeError("API not connected. Call connect() first.")

        try:
            url = f"{self.base_url}/districts"
            params = {
                'limit': limit,
                'offset': offset
            }

            headers = {
                'Authorization': f'Bearer {self.jwt_token}',
                'x-locale': 'en'
            }

            response = self.session.get(
                url,
                headers=headers,
                params=params,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                # Handle different response structures
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict) and 'districts' in data:
                    return data['districts']
                elif isinstance(data, dict) and 'data' in data:
                    return data['data']
                else:
                    return [data]
            else:
                logger.error("Failed to get districts",
                            environment=self.environment,
                            status_code=response.status_code)
                return []

        except Exception as e:
            logger.error("Error getting districts",
                        environment=self.environment,
                        error=str(e))
            raise

    def get_district(self, district_id: int) -> Optional[Dict[str, Any]]:
        """
        Get specific district by ID

        Args:
            district_id: District ID

        Returns:
            District record or None
        """
        if not self.base_url or not self.jwt_token:
            raise RuntimeError("API not connected. Call connect() first.")

        try:
            url = f"{self.base_url}/districts/{district_id}"

            headers = {
                'Authorization': f'Bearer {self.jwt_token}',
                'x-locale': 'en'
            }

            response = self.session.get(
                url,
                headers=headers,
                timeout=30
            )

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return None
            else:
                logger.error("Failed to get district",
                            environment=self.environment,
                            district_id=district_id,
                            status_code=response.status_code)
                return None

        except Exception as e:
            logger.error("Error getting district",
                        environment=self.environment,
                        district_id=district_id,
                        error=str(e))
            raise

    def get_students(self, district_id: Optional[int] = None,
                     limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get students from API

        Args:
            district_id: Filter by district ID
            limit: Maximum number of results
            offset: Offset for pagination

        Returns:
            List of student records
        """
        if not self.base_url or not self.jwt_token:
            raise RuntimeError("API not connected. Call connect() first.")

        try:
            url = f"{self.base_url}/students"
            params = {
                'limit': limit,
                'offset': offset
            }

            if district_id:
                params['district_id'] = district_id

            headers = {
                'Authorization': f'Bearer {self.jwt_token}',
                'x-locale': 'en'
            }

            response = self.session.get(
                url,
                headers=headers,
                params=params,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                # Handle different response structures
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict) and 'students' in data:
                    return data['students']
                elif isinstance(data, dict) and 'data' in data:
                    return data['data']
                else:
                    return [data]
            else:
                logger.error("Failed to get students",
                            environment=self.environment,
                            status_code=response.status_code)
                return []

        except Exception as e:
            logger.error("Error getting students",
                        environment=self.environment,
                        error=str(e))
            raise

    def search_student(self, search_term: str, district_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Search for students by name, email, or sourcedId

        Args:
            search_term: Search query
            district_id: Filter by district ID

        Returns:
            List of matching student records
        """
        if not self.base_url or not self.jwt_token:
            raise RuntimeError("API not connected. Call connect() first.")

        try:
            url = f"{self.base_url}/students/search"
            params = {
                'q': search_term
            }

            if district_id:
                params['district_id'] = district_id

            headers = {
                'Authorization': f'Bearer {self.jwt_token}',
                'x-locale': 'en'
            }

            response = self.session.get(
                url,
                headers=headers,
                params=params,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict) and 'results' in data:
                    return data['results']
                elif isinstance(data, dict) and 'students' in data:
                    return data['students']
                else:
                    return []
            else:
                logger.error("Failed to search students",
                            environment=self.environment,
                            status_code=response.status_code)
                return []

        except Exception as e:
            logger.error("Error searching students",
                        environment=self.environment,
                        error=str(e))
            raise

    def disconnect(self):
        """Close API session"""
        self.session.close()
        self.base_url = None
        self.jwt_token = None
        logger.info("API connection closed", environment=self.environment)
