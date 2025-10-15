---
id: TASK-STUDENT-SEARCH-UI
title: Enhanced Student Search UI with Multi-Match Handling
type: feature
priority: critical
assignee: agent
phase: 2
estimated_hours: 6
---

## Description
Enhance the student search tool with comprehensive UI improvements including multi-match handling, parent matching, class enrollment display, data freshness indicators, and raw data debugging view.

## Acceptance Criteria
- [x] Multiple student match handling with selection UI
- [x] Display match count (e.g., "5 students found")
- [x] Student selection cards with distinguishing info (ID, grade, email)
- [x] Raw data viewer showing JSON from both Bookmarked and ClassLink
- [x] ClassLink parent matching using agents[] array (same as ClassLink Import)
- [x] Date formatting with relative time ("2 days ago")
- [x] Color-coded freshness indicators (green/orange/gray)
- [x] Active enrollment count in selection list
- [x] Backend query enhancement to JOIN with OneRosterClass
- [ ] Display enrolled classes under parents section (IN PROGRESS)
- [ ] Show class names, codes, and subjects
- [ ] Integration tests passing

## Completed Work
1. **Multi-match handling**: Shows selection list when multiple students found with same name
2. **Raw data viewer**: Toggle button showing side-by-side JSON from Bookmarked DB and ClassLink API
3. **Parent matching**: Updated ClassLink connector to fetch all users and match parents via agents[] array
4. **Date formatting**: Relative time display with actual date below
5. **Freshness indicators**: Color-coded badges based on last updated date (≤7 days green, ≤30 days orange, >30 days gray)
6. **Enrollment count**: Shows active class count in selection list
7. **Enhanced enrollment query**: Backend now JOINs with OneRosterClass to fetch class names

## In Progress
- Reorganizing UI to display enrolled classes under parents section
- Backend query complete, frontend display needs update

## Dependencies
- TASK-001 (Flask app structure)
- TASK-005 (Bookmarked DB connector)
- ClassLink connector

## Notes
- All database queries are read-only
- Using OneRoster format for consistency
- Integration test validates full workflow including parent/sibling/campus/enrollment data
- ClassLink parent matching follows same pattern as ClassLink Import system
