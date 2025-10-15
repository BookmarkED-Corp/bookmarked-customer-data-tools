# ClassLink Integration Guide

**Quick Reference:** How to fetch ClassLink data in this application

**Complete Technical Details:** See `../sis-integration-system/docs/requirements/CLASSLINK_DYNAMIC_AUTH.md`

---

## Quick Start

### 1. Get Bearer Token

The ClassLink Bearer token is stored in `secrets.yml` as `CLASSLINK_API_KEY`.

**Production:** Retrieved from Kubernetes secret `prod-secret`
**Development:** From ClassLink Developer Portal or `secrets.yml`

### 2. Use ClassLink Helper

```python
from utils.classlink_helper import ClassLinkHelper

# Initialize (loads CLASSLINK_API_KEY from secrets automatically)
helper = ClassLinkHelper()

# Test connection
result = helper.test_connection()
print(result['message'])

# Fetch students for a district
students = helper.get_students(
    oneroster_app_id='XHkpmX1KunU%3D',  # From ClasslinkApplication.oneroster_application_id
    limit=100
)

# Fetch schools
schools = helper.get_schools(oneroster_app_id='XHkpmX1KunU%3D')

# Fetch classes
classes = helper.get_classes(oneroster_app_id='XHkpmX1KunU%3D')

# Validate data quality
validation = helper.validate_district(oneroster_app_id='XHkpmX1KunU%3D')
```

---

## How It Works

ClassLink uses **two-tier authentication**:

```
┌─────────────────────┐
│ Bearer Token        │ ← In secrets.yml (CLASSLINK_API_KEY)
└──────────┬──────────┘
           │ Step 1: Use Bearer token
           ▼
┌─────────────────────┐
│ ClassLink Mgmt API  │ ← GET /v2/applications/{app_id}/server
└──────────┬──────────┘
           │ Step 2: Returns OAuth credentials
           ▼
┌─────────────────────┐
│ OAuth Credentials:  │
│ - endpoint_url      │ ← Fetched at runtime
│ - client_id         │ ← Fetched at runtime
│ - client_secret     │ ← Fetched at runtime
└──────────┬──────────┘
           │ Step 3: Use OAuth 1.0a HMAC-SHA256
           ▼
┌─────────────────────┐
│ OneRoster API       │ ← GET /ims/oneroster/v1p1/users
│ (per district)      │
└─────────────────────┘
```

**Key Insight:** OAuth credentials are **NOT stored in database**. They are fetched dynamically at runtime.

---

## Finding OneRoster Application IDs

OneRoster Application IDs come from the database:

```sql
SELECT
    ca.application_id,
    ca.oneroster_application_id,  -- ← Use this for API calls
    ca.name,
    d.name as district_name
FROM "ClasslinkApplication" ca
LEFT JOIN "ClasslinkDistrict" cd ON cd."classlinkApplicationId" = ca.id
LEFT JOIN "District" d ON cd."districtId" = d.id
WHERE ca.enabled = 'true'
ORDER BY ca.name;
```

**Example Results:**
```
App ID: 150970, OneRoster ID: XHkpmX1KunU%3D, Name: Bookmarked (Follett ISD)
App ID: 136711, OneRoster ID: dpNrZ04iSJM%3D, Name: bookmarked-test-1
App ID: 151988, OneRoster ID: 9L8tYpLC%2Fd4%3D, Name: Bookmarked
```

**Use:** The `oneroster_application_id` (URL-encoded string like `XHkpmX1KunU%3D`)

---

## Using the Connector Directly

If you need more control than the helper provides:

```python
from connectors.classlink import ClassLinkConnector, OneRosterClient
from utils.secrets import get_secret

# Initialize connector
connector = ClassLinkConnector()
bearer_token = get_secret('CLASSLINK_API_KEY')

# Get OAuth credentials for a district
credentials = connector.get_district_credentials(
    bearer_token=bearer_token,
    oneroster_app_id='XHkpmX1KunU%3D'
)

print(f"Endpoint: {credentials['endpoint_url']}")
print(f"Client ID: {credentials['client_id']}")

# Use OneRoster client directly
client = OneRosterClient(
    credentials['client_id'],
    credentials['client_secret']
)

# Make custom requests
data = client.make_request(
    url=f"{credentials['endpoint_url']}/ims/oneroster/v1p1/enrollments",
    params={'limit': 100}
)
```

---

## Testing Connection

To test if your ClassLink integration is working:

```python
from utils.classlink_helper import ClassLinkHelper

helper = ClassLinkHelper()

# Test connection
result = helper.test_connection()

if result['success']:
    print(f"✓ {result['message']}")
    print(f"  Available districts: {result['details']['district_count']}")

    for district in result['details']['districts']:
        print(f"  - {district['name']} (ID: {district['id']})")
else:
    print(f"✗ {result['message']}")
```

---

## Common Issues

### Issue 1: Invalid or Expired Bearer Token

**Error:** `403 - {"message":"Invalid or expired access token","status":0}`

**Solution:** Get a new Bearer token from:
1. ClassLink Developer Portal: https://developer.classlink.com
2. Or Kubernetes: `kubectl get secret prod-secret -n <namespace> -o jsonpath='{.data.CLASSLINK_API_KEY}' | base64 --decode`

Update `secrets.yml`:
```yaml
CLASSLINK_API_KEY: "your-new-bearer-token-here"
```

### Issue 2: Wrong OneRoster Application ID

**Error:** `404 - Cannot GET /v2/applications/{id}/server`

**Solution:** Make sure you're using `oneroster_application_id` (URL-encoded string) from the database, not `application_id` (integer).

**Correct:** `XHkpmX1KunU%3D`
**Wrong:** `150970`

### Issue 3: OAuth Signature Mismatch

**Error:** `401 - Unauthorized` when calling OneRoster API

**Solution:** The OAuth 1.0a signature generation is very sensitive. Check:
- Using HMAC-SHA256 (not HMAC-SHA1)
- All parameters are URL-encoded
- Parameter string is double-encoded in signature base
- Signing key ends with `&`

---

## Data Caching

The connector caches OAuth credentials in memory to avoid repeated API calls:

```python
# First call: Fetches from ClassLink API
students = helper.get_students(oneroster_app_id='XHkpmX1KunU%3D')

# Second call: Uses cached credentials (faster)
schools = helper.get_schools(oneroster_app_id='XHkpmX1KunU%3D')
```

Cache is per-instance and persists for the lifetime of the application.

---

## Implementation Files

**Helper Utility:** `src/utils/classlink_helper.py`
- Simplified interface for fetching ClassLink data
- Comprehensive documentation and examples

**Connector:** `src/connectors/classlink.py`
- `ClassLinkConnector` - ClassLink Management API client
- `OneRosterClient` - OAuth 1.0a authentication for OneRoster

**Secrets:** `secrets.yml`
- `CLASSLINK_API_KEY` - Bearer token for ClassLink Management API
- `CLASSLINK_API_URL` - Base URL (default: https://nodeapi.classlink.com/v2)

---

## Complete Technical Documentation

For complete implementation details including:
- OAuth 1.0a signature generation algorithm
- Production code comparison
- Step-by-step authentication flow
- Common mistakes and solutions
- Testing strategies

See: `../sis-integration-system/docs/requirements/CLASSLINK_DYNAMIC_AUTH.md`

---

**Last Updated:** 2025-10-14
**Reference Implementation:** `src/connectors/classlink.py`, `src/utils/classlink_helper.py`
