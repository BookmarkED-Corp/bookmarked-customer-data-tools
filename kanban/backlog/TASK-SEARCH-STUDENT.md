---
id: TASK-SEARCH-STUDENT
title: Implement student search with enrollment and school comparison
type: feature
priority: high
assignee: unassigned
parent_task: TASK-DIAGNOSTIC-SEARCH
phase: 2
estimated_hours: 4
---

## Description
Build student search functionality that retrieves student data from both source (ClassLink/OneRoster) and Bookmarked API, then displays side-by-side comparison including enrollments, classes, and school information.

## Features
1. **Search Input**: Name, email, or external ID
2. **Source Data**: Fetch from ClassLink API or OneRoster file
3. **Bookmarked Data**: Fetch from OneShelf API
4. **Display**:
   - Student demographics (name, grade, email, ID)
   - Current school and campus
   - Enrollments (classes, teachers, schedules)
   - Class details (subject, period, teacher)
5. **Historical Data**: For ClassLink, show changes over time from snapshot DB

## Data Relationships
- Student → School (current enrollment)
- Student → Classes (via enrollments table)
- Student → Teachers (via class enrollments)
- Student → Parents (family relationships)

## Acceptance Criteria
- [ ] Search by name, email, or external ID
- [ ] Display student demographics side-by-side
- [ ] Show all enrollments with class and teacher info
- [ ] Highlight data mismatches (missing, different, or extra)
- [ ] For ClassLink: display historical changes
- [ ] Handle students with no enrollments
- [ ] Handle students in multiple schools
- [ ] Performance: < 3 seconds for search + comparison
