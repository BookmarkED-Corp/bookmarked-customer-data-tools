"""
ClassLink API Connector

Connector for ClassLink SIS integration platform.
"""
import requests
from typing import Dict, Any, List, Optional
import structlog

logger = structlog.get_logger(__name__)


class ClassLinkConnector:
    """Connector for ClassLink API"""

    def __init__(self, api_url: str = 'https://api.classlink.com/v2'):
        """
        Initialize ClassLink connector

        Args:
            api_url: Base URL for ClassLink API
        """
        self.api_url = api_url.rstrip('/')

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

            # Test connection by getting district info
            response = requests.get(
                f'{self.api_url}/my/info',
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                district_data = response.json()

                logger.info("ClassLink connection test successful",
                           district_id=district_data.get('districtId'),
                           district_name=district_data.get('districtName'))

                return {
                    'success': True,
                    'message': 'Connected to ClassLink successfully',
                    'details': {
                        'district_id': district_data.get('districtId'),
                        'district_name': district_data.get('districtName'),
                        'tenant_id': district_data.get('tenantId')
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

    def get_schools(self, api_key: str, limit: int = 100) -> List[Dict]:
        """
        Get all schools/orgs from ClassLink

        Args:
            api_key: ClassLink API key
            limit: Maximum number of results (default 100)

        Returns:
            List of school dictionaries
        """
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

        try:
            response = requests.get(
                f'{self.api_url}/orgs',
                headers=headers,
                params={'limit': limit},
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                schools = data.get('orgs', [])
                logger.info("Retrieved ClassLink schools", count=len(schools))
                return schools
            else:
                logger.error("Failed to get ClassLink schools",
                            status_code=response.status_code)
                return []

        except Exception as e:
            logger.error("Error getting ClassLink schools", error=str(e))
            return []

    def get_students(self, api_key: str, school_id: Optional[str] = None,
                    limit: int = 1000) -> List[Dict]:
        """
        Get students from ClassLink

        Args:
            api_key: ClassLink API key
            school_id: Optional school ID to filter by
            limit: Maximum number of results (default 1000)

        Returns:
            List of student dictionaries
        """
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

        params = {'limit': limit}
        if school_id:
            params['schoolSourcedId'] = school_id

        try:
            response = requests.get(
                f'{self.api_url}/users',
                headers=headers,
                params=params,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                users = data.get('users', [])
                # Filter for students only
                students = [u for u in users if u.get('role') == 'student']
                logger.info("Retrieved ClassLink students", count=len(students))
                return students
            else:
                logger.error("Failed to get ClassLink students",
                            status_code=response.status_code)
                return []

        except Exception as e:
            logger.error("Error getting ClassLink students", error=str(e))
            return []

    def get_teachers(self, api_key: str, school_id: Optional[str] = None,
                    limit: int = 1000) -> List[Dict]:
        """
        Get teachers from ClassLink

        Args:
            api_key: ClassLink API key
            school_id: Optional school ID to filter by
            limit: Maximum number of results (default 1000)

        Returns:
            List of teacher dictionaries
        """
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

        params = {'limit': limit}
        if school_id:
            params['schoolSourcedId'] = school_id

        try:
            response = requests.get(
                f'{self.api_url}/users',
                headers=headers,
                params=params,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                users = data.get('users', [])
                # Filter for teachers only
                teachers = [u for u in users if u.get('role') == 'teacher']
                logger.info("Retrieved ClassLink teachers", count=len(teachers))
                return teachers
            else:
                logger.error("Failed to get ClassLink teachers",
                            status_code=response.status_code)
                return []

        except Exception as e:
            logger.error("Error getting ClassLink teachers", error=str(e))
            return []

    def get_classes(self, api_key: str, school_id: Optional[str] = None,
                   limit: int = 1000) -> List[Dict]:
        """
        Get classes/courses from ClassLink

        Args:
            api_key: ClassLink API key
            school_id: Optional school ID to filter by
            limit: Maximum number of results (default 1000)

        Returns:
            List of class dictionaries
        """
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

        params = {'limit': limit}
        if school_id:
            params['schoolSourcedId'] = school_id

        try:
            response = requests.get(
                f'{self.api_url}/classes',
                headers=headers,
                params=params,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                classes = data.get('classes', [])
                logger.info("Retrieved ClassLink classes", count=len(classes))
                return classes
            else:
                logger.error("Failed to get ClassLink classes",
                            status_code=response.status_code)
                return []

        except Exception as e:
            logger.error("Error getting ClassLink classes", error=str(e))
            return []

    def get_enrollments(self, api_key: str, class_id: Optional[str] = None,
                       limit: int = 1000) -> List[Dict]:
        """
        Get enrollments from ClassLink

        Args:
            api_key: ClassLink API key
            class_id: Optional class ID to filter by
            limit: Maximum number of results (default 1000)

        Returns:
            List of enrollment dictionaries
        """
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

        params = {'limit': limit}
        if class_id:
            params['classSourcedId'] = class_id

        try:
            response = requests.get(
                f'{self.api_url}/enrollments',
                headers=headers,
                params=params,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                enrollments = data.get('enrollments', [])
                logger.info("Retrieved ClassLink enrollments", count=len(enrollments))
                return enrollments
            else:
                logger.error("Failed to get ClassLink enrollments",
                            status_code=response.status_code)
                return []

        except Exception as e:
            logger.error("Error getting ClassLink enrollments", error=str(e))
            return []

    def get_student_by_id(self, api_key: str, student_id: str) -> Optional[Dict]:
        """
        Get a specific student by ID

        Args:
            api_key: ClassLink API key
            student_id: Student sourcedId

        Returns:
            Student dictionary or None
        """
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

        try:
            response = requests.get(
                f'{self.api_url}/users/{student_id}',
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                return data.get('user')
            else:
                logger.error("Failed to get ClassLink student",
                            student_id=student_id,
                            status_code=response.status_code)
                return None

        except Exception as e:
            logger.error("Error getting ClassLink student", student_id=student_id, error=str(e))
            return None

    def validate_data_quality(self, api_key: str) -> Dict[str, Any]:
        """
        Validate ClassLink data quality and completeness

        Checks for:
        - Schools exist
        - Students have required fields
        - Teachers have required fields
        - Classes have enrollments
        - Data consistency

        Args:
            api_key: ClassLink API key

        Returns:
            Dict with validation results
        """
        logger.info("Starting ClassLink data quality validation")

        validation_results = {
            'success': True,
            'errors': [],
            'warnings': [],
            'stats': {}
        }

        try:
            # Check schools
            schools = self.get_schools(api_key, limit=100)
            validation_results['stats']['schools_count'] = len(schools)

            if len(schools) == 0:
                validation_results['errors'].append('No schools found in ClassLink')
                validation_results['success'] = False

            # Check students
            students = self.get_students(api_key, limit=100)
            validation_results['stats']['students_count'] = len(students)

            if len(students) == 0:
                validation_results['warnings'].append('No students found in ClassLink')

            # Validate student data quality
            students_missing_email = 0
            students_missing_name = 0
            students_missing_grade = 0

            for student in students[:50]:  # Sample first 50
                if not student.get('email'):
                    students_missing_email += 1
                if not student.get('givenName') or not student.get('familyName'):
                    students_missing_name += 1
                if not student.get('grade'):
                    students_missing_grade += 1

            if students_missing_email > 0:
                validation_results['warnings'].append(
                    f'{students_missing_email} students missing email addresses (sample of 50)'
                )

            if students_missing_name > 0:
                validation_results['warnings'].append(
                    f'{students_missing_name} students missing name fields (sample of 50)'
                )

            if students_missing_grade > 0:
                validation_results['warnings'].append(
                    f'{students_missing_grade} students missing grade level (sample of 50)'
                )

            # Check teachers
            teachers = self.get_teachers(api_key, limit=100)
            validation_results['stats']['teachers_count'] = len(teachers)

            if len(teachers) == 0:
                validation_results['warnings'].append('No teachers found in ClassLink')

            # Check classes
            classes = self.get_classes(api_key, limit=100)
            validation_results['stats']['classes_count'] = len(classes)

            if len(classes) == 0:
                validation_results['warnings'].append('No classes found in ClassLink')

            # Check enrollments
            enrollments = self.get_enrollments(api_key, limit=100)
            validation_results['stats']['enrollments_count'] = len(enrollments)

            if len(enrollments) == 0:
                validation_results['warnings'].append('No enrollments found in ClassLink')

            # Data consistency checks
            if len(classes) > 0 and len(enrollments) == 0:
                validation_results['errors'].append(
                    'Classes exist but no enrollments found - data may be incomplete'
                )
                validation_results['success'] = False

            if len(students) > 0 and len(enrollments) == 0:
                validation_results['warnings'].append(
                    'Students exist but no enrollments found - students may not be assigned to classes'
                )

            logger.info("ClassLink data quality validation completed",
                       success=validation_results['success'],
                       errors=len(validation_results['errors']),
                       warnings=len(validation_results['warnings']))

        except Exception as e:
            logger.error("Error during ClassLink data validation", error=str(e))
            validation_results['success'] = False
            validation_results['errors'].append(f'Validation failed: {str(e)}')

        return validation_results
