---
id: TASK-SEARCH-TEACHER
title: Implement teacher search with classes and schools
type: feature
priority: high
assignee: unassigned
parent_task: TASK-DIAGNOSTIC-SEARCH
phase: 2
estimated_hours: 3
---

## Description
Build teacher search functionality to find teachers and display their class assignments and school relationships, comparing source data with Bookmarked API data.

## Features
1. **Search Input**: Teacher name or email
2. **Source Data**: Fetch teacher from ClassLink/OneRoster
3. **Bookmarked Data**: Fetch from OneShelf API
4. **Display**:
   - Teacher contact information
   - Assigned classes (subject, period, grade level)
   - School assignments
   - Student count per class
   - Schedule information

## Data Relationships
- Teacher → Classes (teaching assignments)
- Teacher → Schools (one or multiple campuses)
- Teacher → Students (via class rosters)
- Class → School
- Class → Students (enrollment count)

## Acceptance Criteria
- [ ] Search by teacher name or email
- [ ] Display teacher information side-by-side
- [ ] Show all assigned classes with details
- [ ] Display school assignments
- [ ] Show student counts per class
- [ ] Highlight missing or mismatched classes
- [ ] Handle teachers at multiple schools
- [ ] Handle teachers with no class assignments
