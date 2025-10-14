---
id: TASK-005
title: Implement customer integration settings framework
type: feature
priority: high
assignee: agent
phase: 1
estimated_hours: 5
---

## Description
Create the Customer model and JSON-based configuration system for storing customer integration settings. Implement loading, validation, and management of customer configs from `customer-integration-settings/` directory.

## Acceptance Criteria
- [ ] `Customer` model created in `src/models/customer.py`
- [ ] JSON schema defined for customer configs
- [ ] `Customer.load(customer_id)` class method implemented
- [ ] Configuration validation on load
- [ ] Template file created at `customer-integration-settings/template.json`
- [ ] Support for ClassLink, OneRoster, and FTP configurations
- [ ] `get_source_connector()` method returns appropriate connector
- [ ] Environment selection (staging/production) working
- [ ] Active/inactive customer status handling
- [ ] Configuration caching (1 hour TTL)

## Dependencies
- TASK-001

## Notes
- Store credential references only, not actual credentials
- Validate JSON against schema before loading
- Support for multiple integration types per customer
- Include sample customer configs for testing
