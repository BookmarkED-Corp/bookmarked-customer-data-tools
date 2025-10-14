---
id: TASK-021
title: Implement Parent Email Conflict Detector tool
type: feature
priority: high
assignee: agent
phase: 3
estimated_hours: 7
---

## Description
Create diagnostic tool for identifying parent email conflicts where multiple parents share the same email address, causing data overwrite issues.

## Acceptance Criteria
- [ ] `ParentConflictTool` class created extending `BaseTool`
- [ ] Input fields: parent_email, district_id
- [ ] Source data query finding all parents with email
- [ ] Bookmarked data query for parent records
- [ ] Identify name mismatches for same email
- [ ] Identify conflicting student assignments
- [ ] Determine if parents are distinct individuals
- [ ] Status determination and conflict classification
- [ ] Remediation suggestions for resolving conflicts
- [ ] Unit tests covering multiple conflict scenarios

## Dependencies
- TASK-006
- TASK-013
- TASK-014

## Notes
- Check for case-insensitive email matches
- Consider email aliases (+ addressing)
- Look for historical data showing changes
- Suggest email consolidation or separation strategies
