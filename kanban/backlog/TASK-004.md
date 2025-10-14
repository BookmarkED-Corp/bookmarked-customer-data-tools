---
id: TASK-004
title: Create Bookmarked production database connector
type: feature
priority: high
assignee: agent
phase: 1
estimated_hours: 4
---

## Description
Implement read-only PostgreSQL connector for Bookmarked production database with additional security controls and audit logging. Should extend or mirror staging connector with enhanced security features.

## Acceptance Criteria
- [ ] Production database configuration added to `BookmarkedDB` class
- [ ] Separate read-only credentials for production
- [ ] Connection timeout reduced to 15 seconds for production
- [ ] Additional authentication layer verified
- [ ] Audit logging enabled for all production queries
- [ ] Query rate limiting implemented (100 queries/min per user)
- [ ] Environment selection parameter working
- [ ] Connection test validates production access
- [ ] All security controls documented

## Dependencies
- TASK-003

## Notes
- Require elevated permissions for production access
- Log all production database queries with user info
- Implement query allowlist for production
- Consider adding query approval workflow
