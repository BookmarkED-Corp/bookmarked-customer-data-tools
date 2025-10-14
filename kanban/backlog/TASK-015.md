---
id: TASK-015
title: Create tool selection and execution UI
type: feature
priority: high
assignee: agent
phase: 2
estimated_hours: 6
---

## Description
Build the UI for selecting and executing diagnostic tools. Include tool input forms, progress indicators during execution, and clear display of tool parameters and descriptions.

## Acceptance Criteria
- [ ] Tool selection page showing all available tools
- [ ] Tool cards with name, description, and use case
- [ ] Dynamic input forms based on `tool.get_inputs()`
- [ ] Form validation before submission
- [ ] Customer/district selector dropdown
- [ ] Environment selector (staging/production)
- [ ] Progress indicator during tool execution
- [ ] Error handling and display for tool failures
- [ ] "Run Another" option after completion
- [ ] Responsive design for mobile devices

## Dependencies
- TASK-007
- TASK-011
- TASK-012

## Notes
- Use AJAX for async tool execution
- Show estimated execution time
- Allow canceling long-running tools
- Provide helpful input validation messages
