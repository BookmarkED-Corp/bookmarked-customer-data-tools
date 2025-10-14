---
id: TASK-007
title: Build basic UI with dashboard and navigation
type: feature
priority: high
assignee: agent
phase: 1
estimated_hours: 5
---

## Description
Create the base HTML templates with Bootstrap, navigation structure, and dashboard page. Implement responsive design and mobile-friendly layout.

## Acceptance Criteria
- [ ] `base.html` template created with navigation bar
- [ ] Bootstrap 5.x integrated
- [ ] Dashboard route created in `src/routes/dashboard.py`
- [ ] `dashboard.html` template with quick stats section
- [ ] Navigation links to Tools, Settings, HubSpot sections
- [ ] Responsive design working on mobile
- [ ] Login/logout links in navigation
- [ ] User role displayed in navigation
- [ ] Static assets directory structure created
- [ ] CSS and JavaScript organized properly

## Dependencies
- TASK-001
- TASK-002

## Notes
- Use Bootstrap for consistent styling
- Consider dark mode support
- Add loading indicators for async operations
- Include footer with version info
