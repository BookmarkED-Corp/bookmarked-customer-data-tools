---
id: TASK-019
title: Create customer integration settings management UI
type: feature
priority: medium
assignee: agent
phase: 2
estimated_hours: 6
---

## Description
Build UI for viewing, adding, and editing customer integration configurations. Allow testing connections to customer source data and managing active/inactive status.

## Acceptance Criteria
- [ ] Customer list page showing all customers
- [ ] Search/filter customers by name or district
- [ ] Add new customer form with template
- [ ] Edit existing customer configuration
- [ ] View customer details (read-only)
- [ ] Test connection button for each integration type
- [ ] Active/inactive toggle
- [ ] Validation of JSON configuration
- [ ] Import/export customer configs (JSON)
- [ ] Audit log of configuration changes

## Dependencies
- TASK-005
- TASK-007

## Notes
- Prevent editing credentials in UI (only references)
- Show last successful connection test
- Include configuration validation before save
- Consider git commit on configuration changes
