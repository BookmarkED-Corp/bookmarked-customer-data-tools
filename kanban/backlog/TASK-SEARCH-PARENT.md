---
id: TASK-SEARCH-PARENT
title: Implement parent search with related students
type: feature
priority: high
assignee: unassigned
parent_task: TASK-DIAGNOSTIC-SEARCH
phase: 2
estimated_hours: 3
---

## Description
Build parent search functionality to find parents and display their relationships with students, comparing source data with Bookmarked API data.

## Features
1. **Search Input**: Parent name or email
2. **Source Data**: Fetch parent from ClassLink/OneRoster
3. **Bookmarked Data**: Fetch from OneShelf API
4. **Display**:
   - Parent contact information
   - Related students (all children)
   - Student demographics and schools
   - Relationship type (mother, father, guardian, etc.)

## Data Relationships
- Parent → Students (family relationships)
- Parent → Contact info (email, phone, address)
- Student → School (via parent's children)

## Acceptance Criteria
- [ ] Search by parent name or email
- [ ] Display parent contact information side-by-side
- [ ] Show all related students with links
- [ ] Display relationship types
- [ ] Highlight missing or mismatched students
- [ ] Handle parents with multiple students
- [ ] Handle orphaned parent records (parent with no students)
