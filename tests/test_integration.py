"""
Integration tests for Customer Data Tools endpoints

These tests verify the complete workflow of:
1. Getting districts from staging/production
2. Validating ClassLink data for districts
3. Searching for students in the database
"""
import pytest
import requests
import json

BASE_URL = "http://localhost:6001"

class TestDistrictEndpoints:
    """Test district-related endpoints"""

    def test_get_districts_staging(self):
        """Test getting districts from staging environment"""
        response = requests.get(f"{BASE_URL}/api/districts?environment=staging")
        assert response.status_code == 200

        data = response.json()
        assert data['success'] is True
        assert 'districts' in data
        assert len(data['districts']) > 0

        # Verify district structure
        district = data['districts'][0]
        assert 'id' in district
        assert 'name' in district
        assert 'createdAt' in district

    def test_get_districts_production(self):
        """Test getting districts from production environment"""
        response = requests.get(f"{BASE_URL}/api/districts?environment=production")
        assert response.status_code == 200

        data = response.json()
        assert data['success'] is True
        assert 'districts' in data


class TestClassLinkValidation:
    """Test ClassLink validation endpoints"""

    def test_classlink_validation_with_data(self):
        """Test ClassLink validation for district with data (Troy ISD)"""
        district_id = 496  # Troy ISD - known to have ClassLink data
        response = requests.get(
            f"{BASE_URL}/api/districts/{district_id}/classlink?environment=staging"
        )
        assert response.status_code == 200

        data = response.json()
        assert data['success'] is True
        assert data['has_classlink_data'] is True
        assert data['classlink_info'] is not None
        assert 'lastSync' in data['classlink_info']

    def test_classlink_validation_without_data(self):
        """Test ClassLink validation for district without data (Abilene ISD)"""
        district_id = 4  # Abilene ISD - known to NOT have ClassLink data
        response = requests.get(
            f"{BASE_URL}/api/districts/{district_id}/classlink?environment=staging"
        )
        assert response.status_code == 200

        data = response.json()
        assert data['success'] is True
        assert data['has_classlink_data'] is False
        assert data['classlink_info'] is None


class TestStudentSearch:
    """Test student search endpoints"""

    def test_student_search_found(self):
        """Test searching for existing student"""
        search_data = {
            'search_term': 'Levi Zaruba',
            'district_id': 496,  # Troy ISD
            'environment': 'staging'
        }

        response = requests.post(
            f"{BASE_URL}/api/students/search",
            json=search_data,
            headers={'Content-Type': 'application/json'}
        )
        assert response.status_code == 200

        data = response.json()
        assert data['success'] is True
        assert data['student'] is True
        assert 'bookmarked_data' in data

        # Verify student data structure
        student = data['bookmarked_data']
        assert student['givenName'] == 'Levi'
        assert student['familyName'] == 'Zaruba'
        assert student['sourcedId'] == '600604'
        assert 'email' in student
        assert 'grade' in student
        assert 'campus' in student

    def test_student_search_not_found(self):
        """Test searching for non-existent student"""
        search_data = {
            'search_term': 'Nonexistent Student XYZ',
            'district_id': 496,
            'environment': 'staging'
        }

        response = requests.post(
            f"{BASE_URL}/api/students/search",
            json=search_data,
            headers={'Content-Type': 'application/json'}
        )
        assert response.status_code == 200

        data = response.json()
        # Should return success=False or student=False
        assert data.get('student') is False or data.get('success') is False

    def test_student_search_missing_params(self):
        """Test student search with missing required parameters"""
        search_data = {
            'search_term': 'Test'
            # Missing district_id
        }

        response = requests.post(
            f"{BASE_URL}/api/students/search",
            json=search_data,
            headers={'Content-Type': 'application/json'}
        )
        assert response.status_code == 400


class TestPageRendering:
    """Test that pages render correctly"""

    def test_district_select_page(self):
        """Test district selection page loads"""
        response = requests.get(f"{BASE_URL}/district-select")
        assert response.status_code == 200
        assert 'District Selection' in response.text

    def test_student_search_page(self):
        """Test student search page loads"""
        response = requests.get(f"{BASE_URL}/tools/student-search")
        assert response.status_code == 200
        assert 'Find Student' in response.text


if __name__ == '__main__':
    # Run tests with verbose output
    pytest.main([__file__, '-v', '-s'])
