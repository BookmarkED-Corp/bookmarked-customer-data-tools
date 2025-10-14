---
id: TASK-003
title: Create Bookmarked staging database connector
type: feature
priority: high
assignee: agent
phase: 1
estimated_hours: 5
---

## Description
Implement read-only PostgreSQL connector for Bookmarked staging database. Create connection pooling, query methods for common data patterns, and environment-specific configuration.

## Acceptance Criteria
- [ ] `BookmarkedDB` class created in `src/connectors/bookmarked_db.py`
- [ ] SQLAlchemy connection pool configured (5 connections max)
- [ ] Read-only database user verification
- [ ] Connection timeout set to 30 seconds
- [ ] Query methods implemented: `get_students()`, `get_classes()`, `get_enrollments()`, `get_organizations()`
- [ ] Environment selection (staging) working
- [ ] Error handling for connection failures
- [ ] Connection test method implemented
- [ ] Credentials loaded from environment variables

## Dependencies
- TASK-001

## Notes
- Use SQLAlchemy for connection management
- Implement automatic connection retry with exponential backoff
- Log all queries for debugging
- Ensure all database operations are read-only
