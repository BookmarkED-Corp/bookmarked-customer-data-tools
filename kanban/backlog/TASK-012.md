---
id: TASK-012
title: Implement Missing Data Finder tool
type: feature
priority: critical
assignee: agent
phase: 2
estimated_hours: 8
---

## Description
Create the Missing Data Finder tool for identifying missing students, classes, or enrollments. Compare source data with Bookmarked to find what didn't import correctly.

## Acceptance Criteria
- [ ] `MissingDataTool` class created extending `BaseTool`
- [ ] Input fields: student_name (or class_name), school, district_id
- [ ] Search source data for student/class existence
- [ ] Search Bookmarked data for same entities
- [ ] Identify missing elements (student, classes, enrollments, teacher assignments)
- [ ] Check import logs for error messages
- [ ] Status report showing what's missing and why
- [ ] Remediation suggestions for importing missing data
- [ ] Support for bulk checking multiple students
- [ ] Tests covering various missing data scenarios

## Dependencies
- TASK-006
- TASK-005

## Notes
- Check enrollment status in source data
- Verify enrollment date ranges
- Check for archived/inactive students
- Include teacher assignment validation
