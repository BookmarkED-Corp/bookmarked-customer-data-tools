---
id: TASK-023
title: Implement HubSpot OAuth2 integration
type: feature
priority: high
assignee: agent
phase: 3
estimated_hours: 6
---

## Description
Set up HubSpot OAuth2 authentication flow for obtaining bearer tokens, implement token refresh handling, and store tokens securely per user session.

## Acceptance Criteria
- [ ] `HubSpotConnector` class created in `src/connectors/hubspot.py`
- [ ] OAuth2 authorization flow implemented
- [ ] Callback route for OAuth2 redirect
- [ ] Bearer token storage per user session
- [ ] Token refresh logic when expired
- [ ] Secure token storage (not in cookies)
- [ ] Connection test endpoint
- [ ] Error handling for OAuth failures
- [ ] UI for initiating HubSpot connection
- [ ] Disconnect/revoke token functionality

## Dependencies
- TASK-002
- TASK-008

## Notes
- Follow HubSpot OAuth2 documentation
- Store tokens encrypted in session
- Handle token expiration gracefully
- Log OAuth events for security audit
