#!/usr/bin/env python3
"""
Test ClassLink integration using production sequence

This script replicates the exact sequence used in bookmarked-back production code:
1. Get Bearer token from secrets
2. Call /districts to get list of applications
3. For a specific district, call /v2/applications/{id}/server to get OAuth credentials
4. Use OneRoster OAuth 1.0a to fetch students

Tests with the same production key to ensure compatibility.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.connectors.classlink import ClassLinkConnector, OneRosterClient
from src.utils.secrets import get_secret
import json


def test_production_sequence():
    """Test ClassLink using production sequence"""

    print("=" * 80)
    print("ClassLink Production Sequence Test")
    print("=" * 80)
    print()

    # Step 1: Get Bearer token
    print("Step 1: Loading Bearer token from secrets...")
    bearer_token = get_secret('CLASSLINK_API_KEY')

    if not bearer_token:
        print("❌ ERROR: CLASSLINK_API_KEY not found in secrets.yml")
        print("Please add it to secrets.yml first")
        return False

    print(f"✓ Bearer token loaded: {bearer_token[:20]}...")
    print()

    # Step 2: Test connection (get districts)
    print("Step 2: Testing connection (GET /districts)...")
    connector = ClassLinkConnector()

    result = connector.test_connection(bearer_token)

    if not result['success']:
        print(f"❌ Connection test failed: {result['message']}")
        return False

    print(f"✓ Connection successful!")
    print(f"  Districts available: {result['details']['district_count']}")
    print(f"  Sample districts:")
    for district in result['details'].get('districts', [])[:3]:
        print(f"    - {district['name']} (ID: {district['id']})")
    print()

    # Step 3: Get OAuth credentials for a specific district
    print("Step 3: Getting OAuth credentials for an active district...")

    # Find an active district from the results
    active_district = None
    for dist in result['details'].get('districts', []):
        # Try bookmarked-test-1 first (ID: 136711)
        if dist['id'] == 136711:
            active_district = dist
            break

    if not active_district and result['details'].get('districts'):
        # Fallback to first district
        active_district = result['details']['districts'][0]

    if not active_district:
        print("❌ No districts available to test")
        return False

    # Get the full application details to find oneroster_application_id
    import requests
    headers = {'Authorization': f'Bearer {bearer_token}', 'Content-Type': 'application/json'}
    response = requests.get('https://oneroster-proxy.classlink.io/applications', headers=headers, timeout=10)

    if response.status_code != 200:
        print("❌ Failed to get application list")
        return False

    applications = response.json().get('applications', [])

    # Find our test district
    test_app = next((app for app in applications if app.get('id') == active_district['id']), None)

    if not test_app or not test_app.get('oneroster_application_id'):
        print(f"❌ Could not find oneroster_application_id for district {active_district['name']}")
        return False

    oneroster_app_id = test_app['oneroster_application_id']
    print(f"  Using: {active_district['name']} (OneRoster ID: {oneroster_app_id})")

    creds = connector.get_district_credentials(bearer_token, oneroster_app_id)

    if not creds:
        print(f"❌ Failed to get district credentials")
        return False

    print(f"✓ OAuth credentials retrieved:")
    print(f"  Endpoint URL: {creds['endpoint_url']}")
    print(f"  Client ID: {creds['client_id'][:20]}...")
    print(f"  Client Secret: {creds['client_secret'][:20]}...")
    print()

    # Step 4: Use OneRoster OAuth 1.0a to fetch data
    print("Step 4: Fetching students using OneRoster OAuth 1.0a...")

    client = OneRosterClient(creds['client_id'], creds['client_secret'])

    # Fetch first 10 students
    url = f"{creds['endpoint_url']}/ims/oneroster/v1p1/users"
    params = {'limit': 10, 'offset': 0, 'orderBy': 'asc'}

    data = client.make_request(url, params)

    if not data:
        print(f"❌ Failed to fetch students from OneRoster API")
        return False

    users = data.get('users', [])
    students = [u for u in users if u.get('role') == 'student']

    print(f"✓ Students fetched successfully!")
    print(f"  Total users returned: {len(users)}")
    print(f"  Students: {len(students)}")
    print()

    if students:
        print("  Sample students:")
        for student in students[:3]:
            print(f"    - {student.get('givenName')} {student.get('familyName')} ({student.get('email')})")

    print()
    print("=" * 80)
    print("✓ All tests passed! Production sequence working correctly.")
    print("=" * 80)

    return True


def test_data_validation():
    """Test ClassLink data validation"""

    print()
    print("=" * 80)
    print("ClassLink Data Validation Test")
    print("=" * 80)
    print()

    bearer_token = get_secret('CLASSLINK_API_KEY')
    if not bearer_token:
        print("❌ CLASSLINK_API_KEY not found")
        return False

    connector = ClassLinkConnector()

    # Get active district
    import requests
    headers = {'Authorization': f'Bearer {bearer_token}', 'Content-Type': 'application/json'}
    response = requests.get('https://oneroster-proxy.classlink.io/applications', headers=headers, timeout=10)

    if response.status_code != 200:
        print("❌ Failed to get application list")
        return False

    applications = response.json().get('applications', [])

    # Find an active district (prefer bookmarked-test-1)
    test_app = next((app for app in applications if app.get('id') == 136711), None)

    if not test_app and applications:
        test_app = applications[0]

    if not test_app or not test_app.get('oneroster_application_id'):
        print("❌ No active districts available")
        return False

    oneroster_app_id = test_app['oneroster_application_id']

    print(f"Validating district: {test_app.get('name')} ({oneroster_app_id})")
    print()

    validation = connector.validate_district_data(bearer_token, oneroster_app_id)

    print("Validation Results:")
    print(f"  Success: {validation['success']}")
    print()

    if validation['stats']:
        print("  Statistics:")
        for key, value in validation['stats'].items():
            print(f"    {key}: {value}")
        print()

    if validation['errors']:
        print("  Errors:")
        for error in validation['errors']:
            print(f"    ❌ {error}")
        print()

    if validation['warnings']:
        print("  Warnings:")
        for warning in validation['warnings']:
            print(f"    ⚠️  {warning}")
        print()

    if validation['success'] and not validation['errors']:
        print("✓ Data validation passed!")
        return True
    else:
        print("❌ Data validation failed")
        return False


if __name__ == '__main__':
    print()
    print("Testing ClassLink Integration with Production Key")
    print()

    # Test production sequence
    test1_passed = test_production_sequence()

    # Test data validation
    test2_passed = test_data_validation()

    print()
    print("=" * 80)
    print("Summary:")
    print(f"  Production Sequence Test: {'✓ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"  Data Validation Test: {'✓ PASSED' if test2_passed else '❌ FAILED'}")
    print("=" * 80)
    print()

    sys.exit(0 if (test1_passed and test2_passed) else 1)
