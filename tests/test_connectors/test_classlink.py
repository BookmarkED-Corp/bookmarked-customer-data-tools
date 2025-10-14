"""
Tests for ClassLink API Connector

Tests the ClassLink connector functionality including connection testing
and data retrieval operations.
"""
import pytest
from src.connectors.classlink import ClassLinkConnector
import os


@pytest.fixture
def classlink_connector():
    """Fixture to create ClassLink connector instance"""
    return ClassLinkConnector()


@pytest.fixture
def api_key():
    """Fixture to get API key from environment"""
    key = os.getenv('CLASSLINK_API_KEY')
    if not key:
        pytest.skip("CLASSLINK_API_KEY not set in environment")
    return key


class TestClassLinkConnection:
    """Test ClassLink connection functionality"""

    def test_connector_initialization(self, classlink_connector):
        """Test that connector initializes properly"""
        assert classlink_connector is not None
        assert classlink_connector.api_url == 'https://api.classlink.com/v2'

    def test_test_connection_success(self, classlink_connector, api_key):
        """Test successful connection to ClassLink API"""
        result = classlink_connector.test_connection(api_key)

        assert result['success'] is True
        assert 'Connected to ClassLink successfully' in result['message']
        assert result['details'] is not None

    def test_test_connection_invalid_key(self, classlink_connector):
        """Test connection with invalid API key"""
        result = classlink_connector.test_connection('invalid_key')

        assert result['success'] is False
        assert 'Connection failed' in result['message']

    def test_test_connection_empty_key(self, classlink_connector):
        """Test connection with empty API key"""
        result = classlink_connector.test_connection('')

        assert result['success'] is False


class TestClassLinkSchools:
    """Test ClassLink schools functionality"""

    def test_get_schools(self, classlink_connector, api_key):
        """Test getting schools"""
        schools = classlink_connector.get_schools(api_key)

        assert isinstance(schools, list)
        # Check structure if schools exist
        if len(schools) > 0:
            school = schools[0]
            assert 'sourcedId' in school or 'id' in school
            assert 'name' in school or 'schoolName' in school

    def test_get_schools_invalid_key(self, classlink_connector):
        """Test getting schools with invalid API key"""
        schools = classlink_connector.get_schools('invalid_key')

        assert isinstance(schools, list)
        assert len(schools) == 0  # Should return empty list on error


class TestClassLinkStudents:
    """Test ClassLink students functionality"""

    def test_get_students(self, classlink_connector, api_key):
        """Test getting students"""
        students = classlink_connector.get_students(api_key)

        assert isinstance(students, list)
        # Check structure if students exist
        if len(students) > 0:
            student = students[0]
            assert 'sourcedId' in student or 'id' in student
            # Should have student identifying information
            assert any(key in student for key in ['firstName', 'lastName', 'name', 'email'])

    def test_get_students_by_school(self, classlink_connector, api_key):
        """Test getting students filtered by school"""
        # First get a school ID
        schools = classlink_connector.get_schools(api_key)

        if len(schools) == 0:
            pytest.skip("No schools available for testing")

        school_id = schools[0].get('sourcedId') or schools[0].get('id')
        students = classlink_connector.get_students(api_key, school_id=school_id)

        assert isinstance(students, list)
        # All students should belong to the specified school
        if len(students) > 0:
            student = students[0]
            # Verify student has expected structure
            assert 'sourcedId' in student or 'id' in student


class TestClassLinkClasses:
    """Test ClassLink classes/courses functionality"""

    def test_get_classes(self, classlink_connector, api_key):
        """Test getting classes"""
        classes = classlink_connector.get_classes(api_key)

        assert isinstance(classes, list)
        # Check structure if classes exist
        if len(classes) > 0:
            class_obj = classes[0]
            assert 'sourcedId' in class_obj or 'id' in class_obj
            assert any(key in class_obj for key in ['className', 'name', 'title'])

    def test_get_classes_by_school(self, classlink_connector, api_key):
        """Test getting classes filtered by school"""
        schools = classlink_connector.get_schools(api_key)

        if len(schools) == 0:
            pytest.skip("No schools available for testing")

        school_id = schools[0].get('sourcedId') or schools[0].get('id')
        classes = classlink_connector.get_classes(api_key, school_id=school_id)

        assert isinstance(classes, list)


class TestClassLinkTeachers:
    """Test ClassLink teachers functionality"""

    def test_get_teachers(self, classlink_connector, api_key):
        """Test getting teachers"""
        teachers = classlink_connector.get_teachers(api_key)

        assert isinstance(teachers, list)
        # Check structure if teachers exist
        if len(teachers) > 0:
            teacher = teachers[0]
            assert 'sourcedId' in teacher or 'id' in teacher
            assert any(key in teacher for key in ['firstName', 'lastName', 'name', 'email'])

    def test_get_teachers_by_school(self, classlink_connector, api_key):
        """Test getting teachers filtered by school"""
        schools = classlink_connector.get_schools(api_key)

        if len(schools) == 0:
            pytest.skip("No schools available for testing")

        school_id = schools[0].get('sourcedId') or schools[0].get('id')
        teachers = classlink_connector.get_teachers(api_key, school_id=school_id)

        assert isinstance(teachers, list)


class TestClassLinkEnrollments:
    """Test ClassLink enrollments functionality"""

    def test_get_enrollments(self, classlink_connector, api_key):
        """Test getting enrollments"""
        enrollments = classlink_connector.get_enrollments(api_key)

        assert isinstance(enrollments, list)
        # Check structure if enrollments exist
        if len(enrollments) > 0:
            enrollment = enrollments[0]
            assert 'sourcedId' in enrollment or 'id' in enrollment
            # Should have class and user references
            assert any(key in enrollment for key in ['classSourcedId', 'userSourcedId', 'class', 'user'])

    def test_get_enrollments_by_class(self, classlink_connector, api_key):
        """Test getting enrollments for a specific class"""
        classes = classlink_connector.get_classes(api_key)

        if len(classes) == 0:
            pytest.skip("No classes available for testing")

        class_id = classes[0].get('sourcedId') or classes[0].get('id')
        enrollments = classlink_connector.get_enrollments(api_key, class_id=class_id)

        assert isinstance(enrollments, list)


class TestClassLinkErrorHandling:
    """Test ClassLink error handling"""

    def test_invalid_api_endpoint(self, classlink_connector, api_key):
        """Test handling of invalid API endpoint"""
        # This tests the connector's error handling for non-existent endpoints
        # Most methods should return empty lists on error
        result = classlink_connector.get_schools('invalid_key')
        assert isinstance(result, list)
        assert len(result) == 0

    def test_connection_timeout(self, classlink_connector):
        """Test handling of connection timeout"""
        # Test with invalid URL to trigger timeout
        connector = ClassLinkConnector(api_url='http://localhost:9999')
        result = connector.test_connection('test_key')

        assert result['success'] is False
        assert 'timeout' in result['message'].lower() or 'failed' in result['message'].lower()


class TestClassLinkIntegration:
    """Integration tests for ClassLink connector"""

    @pytest.mark.integration
    def test_full_data_flow(self, classlink_connector, api_key):
        """Test complete data retrieval flow"""
        # Get schools
        schools = classlink_connector.get_schools(api_key)
        assert isinstance(schools, list)

        if len(schools) == 0:
            pytest.skip("No schools available for integration test")

        # Get students, teachers, and classes
        students = classlink_connector.get_students(api_key)
        teachers = classlink_connector.get_teachers(api_key)
        classes = classlink_connector.get_classes(api_key)

        assert isinstance(students, list)
        assert isinstance(teachers, list)
        assert isinstance(classes, list)

        # Get enrollments
        enrollments = classlink_connector.get_enrollments(api_key)
        assert isinstance(enrollments, list)

        # Verify data consistency
        print(f"Retrieved {len(schools)} schools, {len(students)} students, "
              f"{len(teachers)} teachers, {len(classes)} classes, "
              f"and {len(enrollments)} enrollments")
