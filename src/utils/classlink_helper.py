"""
ClassLink Helper Utility

Simplifies fetching ClassLink data for a specific district.

Usage:
    from utils.classlink_helper import ClassLinkHelper

    # Initialize with bearer token (gets from secrets by default)
    helper = ClassLinkHelper()

    # Or provide token explicitly
    helper = ClassLinkHelper(bearer_token='your-token-here')

    # Fetch data for a district (by application ID)
    students = helper.get_students(district_app_id=201087, limit=100)
    schools = helper.get_schools(district_app_id=201087)
    classes = helper.get_classes(district_app_id=201087)

    # Validate district data quality
    validation = helper.validate_district(district_app_id=201087)

    # Get district credentials (endpoint_url, client_id, client_secret)
    creds = helper.get_credentials(district_app_id=201087)

How it works:
    1. Uses the ClassLink Bearer token to call the ClassLink management API
    2. Fetches district-specific OAuth 1.0a credentials (client_id + client_secret)
    3. Uses those credentials to make OneRoster API calls
    4. Caches credentials per district to avoid repeated API calls

    This matches the production backend's approach of dynamically fetching
    credentials at runtime rather than pre-storing them.

Finding District Application IDs:
    District application IDs can be found in the staging/production database:

    SELECT
        ca.application_id,
        ca.name,
        d.name as district_name
    FROM "ClasslinkApplication" ca
    LEFT JOIN "ClasslinkDistrict" cd ON cd."classlinkApplicationId" = ca.id
    LEFT JOIN "District" d ON cd."districtId" = d.id
    WHERE ca.enabled = 'true'
    ORDER BY ca.name;

    Recent districts with data:
    - Follett ISD: 201087
    - DRIPPING SPRINGS ISD: 181294
    - La Grange ISD: 167343
"""
from typing import Dict, Any, List, Optional
import structlog
from src.connectors.classlink import ClassLinkConnector
from src.utils.secrets import get_secret

logger = structlog.get_logger(__name__)


class ClassLinkHelper:
    """
    Simplified interface for fetching ClassLink data for a specific district

    Example:
        # Fetch students for Follett ISD (district_app_id = 201087)
        helper = ClassLinkHelper()
        students = helper.get_students(201087, limit=50)

        for student in students:
            print(f"{student['givenName']} {student['familyName']} - Grade {student.get('grades', ['N/A'])[0]}")
    """

    def __init__(self, bearer_token: Optional[str] = None):
        """
        Initialize ClassLink helper

        Args:
            bearer_token: ClassLink Bearer token (if None, loads from secrets)
        """
        self.bearer_token = bearer_token or get_secret('CLASSLINK_API_KEY')

        if not self.bearer_token:
            raise ValueError(
                "CLASSLINK_API_KEY not found in secrets or environment. "
                "Please set it in secrets.yml or pass bearer_token parameter."
            )

        self.connector = ClassLinkConnector()
        logger.info("ClassLink helper initialized")

    def get_credentials(self, district_app_id: int) -> Optional[Dict[str, Any]]:
        """
        Get OneRoster endpoint and OAuth credentials for a district

        Args:
            district_app_id: District application ID from ClasslinkApplication table

        Returns:
            Dict with endpoint_url, client_id, client_secret or None

        Example:
            creds = helper.get_credentials(201087)
            print(f"Endpoint: {creds['endpoint_url']}")
            print(f"Client ID: {creds['client_id']}")
        """
        return self.connector.get_district_credentials(self.bearer_token, district_app_id)

    def get_students(self, district_app_id: int, limit: int = 100, offset: int = 0) -> List[Dict]:
        """
        Get students for a district

        Args:
            district_app_id: District application ID
            limit: Maximum number of results (default 100)
            offset: Pagination offset (default 0)

        Returns:
            List of student dictionaries with fields:
            - sourcedId: Student ID
            - givenName, familyName: Name
            - email: Email address
            - grades: List of grade levels
            - role: Should be 'student'

        Example:
            students = helper.get_students(201087, limit=10)
            for s in students:
                print(f"{s['givenName']} {s['familyName']} ({s.get('email', 'No email')})")
        """
        return self.connector.get_students(self.bearer_token, district_app_id, limit, offset)

    def get_schools(self, district_app_id: int, limit: int = 100, offset: int = 0) -> List[Dict]:
        """
        Get schools/organizations for a district

        Args:
            district_app_id: District application ID
            limit: Maximum number of results (default 100)
            offset: Pagination offset (default 0)

        Returns:
            List of organization dictionaries with fields:
            - sourcedId: Organization ID
            - name: School/district name
            - type: 'school' or 'district'
            - identifier: External identifier

        Example:
            schools = helper.get_schools(201087)
            for school in schools:
                print(f"{school['name']} ({school['type']})")
        """
        return self.connector.get_schools(self.bearer_token, district_app_id, limit, offset)

    def get_classes(self, district_app_id: int, limit: int = 100, offset: int = 0) -> List[Dict]:
        """
        Get classes for a district

        Args:
            district_app_id: District application ID
            limit: Maximum number of results (default 100)
            offset: Pagination offset (default 0)

        Returns:
            List of class dictionaries with fields:
            - sourcedId: Class ID
            - title: Class name
            - classCode: Class code
            - classType: Type of class
            - periods: Class periods

        Example:
            classes = helper.get_classes(201087)
            for cls in classes:
                print(f"{cls.get('title', 'Unnamed')} ({cls.get('classCode', 'N/A')})")
        """
        return self.connector.get_classes(self.bearer_token, district_app_id, limit, offset)

    def validate_district(self, district_app_id: int) -> Dict[str, Any]:
        """
        Validate data quality for a district

        Checks:
        - Can we get credentials?
        - Do schools exist?
        - Do students exist?
        - Are students missing required fields?
        - Do classes exist?

        Args:
            district_app_id: District application ID

        Returns:
            Dict with validation results:
            - success: bool
            - errors: List of error messages
            - warnings: List of warning messages
            - stats: Dict with counts (schools_count, students_count, classes_count)

        Example:
            result = helper.validate_district(201087)
            if result['success']:
                print(f"✓ Validation passed")
                print(f"  Schools: {result['stats']['schools_count']}")
                print(f"  Students: {result['stats']['students_count']}")
            else:
                print(f"✗ Validation failed: {result['errors']}")
        """
        return self.connector.validate_district_data(self.bearer_token, district_app_id)

    def test_connection(self) -> Dict[str, Any]:
        """
        Test the ClassLink API connection

        Returns:
            Dict with connection test results:
            - success: bool
            - message: str
            - details: Dict with district_count and list of districts

        Example:
            result = helper.test_connection()
            if result['success']:
                print(f"✓ {result['message']}")
                print(f"  Available districts: {len(result['details']['districts'])}")
        """
        return self.connector.test_connection(self.bearer_token)


# Convenience function for quick access
def fetch_classlink_data(district_app_id: int, data_type: str = 'students',
                         bearer_token: Optional[str] = None,
                         limit: int = 100) -> List[Dict]:
    """
    Quick convenience function to fetch ClassLink data

    Args:
        district_app_id: District application ID
        data_type: Type of data to fetch ('students', 'schools', 'classes')
        bearer_token: Optional bearer token (loads from secrets if not provided)
        limit: Maximum results (default 100)

    Returns:
        List of data dictionaries

    Example:
        # Get 50 students for Follett ISD
        students = fetch_classlink_data(201087, 'students', limit=50)

        # Get all schools for DRIPPING SPRINGS ISD
        schools = fetch_classlink_data(181294, 'schools')
    """
    helper = ClassLinkHelper(bearer_token)

    if data_type == 'students':
        return helper.get_students(district_app_id, limit=limit)
    elif data_type == 'schools':
        return helper.get_schools(district_app_id, limit=limit)
    elif data_type == 'classes':
        return helper.get_classes(district_app_id, limit=limit)
    else:
        raise ValueError(f"Invalid data_type: {data_type}. Must be 'students', 'schools', or 'classes'")
