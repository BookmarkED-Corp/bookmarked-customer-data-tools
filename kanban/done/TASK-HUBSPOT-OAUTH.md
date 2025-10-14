---
id: TASK-HUBSPOT-OAUTH
title: Implement HubSpot OAuth2 authentication flow
type: feature
priority: high
assignee: agent
phase: 1
estimated_hours: 3
completed: 2025-10-14
---

## Description
Implement OAuth2 authentication flow for HubSpot integration using popup window pattern instead of manual token entry.

## Acceptance Criteria
- [x] Created `hubspot_auth.py` with OAuth routes
- [x] `/auth/hubspot/start` route initiates OAuth flow
- [x] `/auth/hubspot/callback` route handles callback and token exchange
- [x] `/api/hubspot/status` route checks authentication status
- [x] Registered hubspot_auth blueprint in routes.py
- [x] Updated connections setup page to use OAuth popup
- [x] Implemented postMessage communication between popup and parent
- [x] Added success/error HTML templates with auto-close
- [x] Tokens stored in Flask session and encrypted when saved
- [x] Origin validation on postMessage for security

## Implementation Details

**OAuth Flow:**
1. User clicks "Connect to HubSpot" → Opens OAuth popup (600x700px)
2. User logs into HubSpot → Authorizes the application
3. HubSpot redirects → Back to `/auth/hubspot/callback` with authorization code
4. Backend exchanges code → For access token using client credentials
5. Success page displays → Sends token to parent via `postMessage`
6. Parent window receives token → Stores it and shows success message
7. Popup auto-closes → After 2 seconds

**Security Features:**
- Origin validation on `postMessage` events
- Authorization code grant flow (OAuth2 standard)
- HTTPS-only OAuth flow (enforced by HubSpot)
- Tokens encrypted when saved to config file
- Session-based token storage

## Files Modified
- `src/routes/hubspot_auth.py` (new)
- `src/api/routes.py` (added blueprint registration)
- `src/templates/connections/setup.html` (replaced manual token input with OAuth button)
- `.env` (updated redirect URI to port 6001)

## Notes
- Follows industry-standard OAuth2 authorization code grant flow
- Popup window pattern provides better UX than redirect flow
- Tokens are encrypted using Fernet encryption when persisted
- Session tokens expire with Flask session timeout
