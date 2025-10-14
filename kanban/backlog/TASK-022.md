---
id: TASK-022
title: Implement Campus Transfer Validator tool
type: feature
priority: high
assignee: agent
phase: 3
estimated_hours: 7
---

## Description
Create diagnostic tool for validating campus transfers, identifying students who transferred campuses but still appear enrolled at old campus (phantom enrollments).

## Acceptance Criteria
- [ ] `CampusTransferTool` class created extending `BaseTool`
- [ ] Input fields: student_name, old_campus, new_campus, district_id
- [ ] Source data verification of current enrollment
- [ ] Bookmarked check for old campus enrollments
- [ ] Verify proper relationship cleanup
- [ ] Identify phantom enrollments and classes
- [ ] Check enrollment date ranges
- [ ] Status report of transfer and cleanup issues
- [ ] Remediation path for removing old enrollments
- [ ] Tests covering various transfer scenarios

## Dependencies
- TASK-006
- TASK-013
- TASK-014

## Notes
- Check transfer effective dates
- Look for overlapping enrollments
- Verify all related data (classes, teachers)
- Consider mid-year transfers
