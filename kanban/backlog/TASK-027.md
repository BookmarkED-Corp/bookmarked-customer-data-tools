---
id: TASK-027
title: Implement HubSpot ticket updating with results
type: feature
priority: high
assignee: agent
phase: 3
estimated_hours: 5
---

## Description
Add functionality to post diagnostic results back to HubSpot tickets as comments and optionally update ticket status based on findings.

## Acceptance Criteria
- [ ] Method to add comment to HubSpot ticket
- [ ] Format diagnostic results for HubSpot comment
- [ ] Include status, findings, and remediation steps
- [ ] Optional ticket status update
- [ ] Link diagnostic run from HubSpot comment
- [ ] Error handling for HubSpot API failures
- [ ] Preview comment before posting
- [ ] UI confirmation before posting
- [ ] Success notification after posting
- [ ] Audit log of HubSpot updates

## Dependencies
- TASK-023
- TASK-016

## Notes
- Format comments for readability in HubSpot
- Include timestamp and user who ran diagnostic
- Make ticket updates optional (user choice)
- Handle HubSpot rate limits
