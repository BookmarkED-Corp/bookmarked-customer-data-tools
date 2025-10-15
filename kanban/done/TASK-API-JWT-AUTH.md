---
id: TASK-API-JWT-AUTH
title: Implement JWT Bearer token authentication for Bookmarked API connections
type: feature
priority: high
assignee: agent
phase: 1
estimated_hours: 3
completed: 2025-10-14
---

## Description
Replace HTTP Basic Authentication with JWT Bearer token authentication for the Bookmarked API connector. The backend API uses JWT tokens obtained through login, not Basic Auth. This task involves implementing the login flow, token management, and updating all API methods to use Bearer tokens.

## Acceptance Criteria
- [x] Implement `_login()` method to obtain JWT tokens from `/auth/` endpoint
- [x] Update `test_connection()` to use JWT authentication
- [x] Update all API methods (`get_districts()`, `get_students()`, etc.) to use Bearer tokens
- [x] Fix login endpoint from `/auth/login` to `/auth/` (matching backend)
- [x] Test endpoint changed to `/auth/health-check`
- [x] Staging API connection test passes (200 OK)
- [x] Production API connection test passes (200 OK)
- [x] All 17 browser tests pass
- [x] Enhanced logging for debugging authentication flow

## Technical Changes

### Files Modified
1. **src/connectors/bookmarked_api.py**
   - Removed `HTTPBasicAuth` import
   - Added `_login()` method for JWT token retrieval
   - Changed `self.auth` to `self.jwt_token`
   - Updated all methods to use `Authorization: Bearer <token>` header
   - Added `x-locale: en` header to match API requirements
   - Fixed login endpoint: `/auth/` (not `/auth/login`)

2. **tests/browser/connections.spec.js**
   - Fixed race condition in status indicator test
   - Improved localStorage clearing to prevent auto-test interference

### API Flow
1. **Login**: POST to `/auth/` with `{email, password}` → receives JWT token
2. **Test**: GET to `/auth/health-check` with `Authorization: Bearer <token>`
3. **All requests**: Include Bearer token in Authorization header

## Test Results
```
Staging API:     ✅ SUCCESS (200 OK, 0.08s response time)
Production API:  ✅ SUCCESS (200 OK, 0.08s response time)
Browser Tests:   ✅ 17/17 PASSED (1.4m)
```

## Dependencies
- Backend API controller at `/auth/` endpoint
- Backend health check at `/auth/health-check`

## Notes
- JWT tokens are session-based, obtained fresh for each connection test
- Token structure: `{token: "eyJhbGciOiJIUzI1...", user: {...}}`
- All API methods now properly authenticated with Bearer tokens
- Auto-testing feature works correctly with JWT authentication
