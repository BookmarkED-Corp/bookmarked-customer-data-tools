---
id: TASK-014
title: Create OneRoster connector (API and CSV)
type: feature
priority: high
assignee: agent
phase: 2
estimated_hours: 8
---

## Description
Implement OneRoster integration supporting both direct API access and CSV file uploads. Include CSV parsing, manifest validation, and schema validation for OneRoster 1.1 and 1.2.

## Acceptance Criteria
- [ ] `OneRosterConnector` class created in `src/connectors/oneroster.py`
- [ ] Direct OneRoster API support with authentication
- [ ] CSV file upload and parsing (ZIP, CSV, XLSX formats)
- [ ] Manifest file validation
- [ ] Schema validation for OneRoster 1.1 and 1.2
- [ ] Methods: `get_students()`, `get_classes()`, `get_enrollments()`, `get_orgs()`
- [ ] CSV parsing handles malformed data gracefully
- [ ] File upload UI for CSV imports
- [ ] Error reporting for validation failures
- [ ] Unit tests for CSV parsing edge cases

## Dependencies
- TASK-005
- TASK-008

## Notes
- Support both OneRoster 1.1 and 1.2 formats
- Handle character encoding issues in CSV files
- Validate required fields per OneRoster spec
- Consider large file handling (streaming)
