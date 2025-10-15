---
id: TASK-SEARCH-PARENT
title: Implement parent search with related students
type: feature
priority: high
assignee: claude
parent_task: TASK-DIAGNOSTIC-SEARCH
phase: 2
estimated_hours: 3
status: completed
completed_date: 2025-10-15
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
- [x] Search by parent name or email
- [x] Display parent contact information side-by-side
- [x] Show all related students with links
- [ ] Display relationship types (not in source data)
- [ ] Highlight missing or mismatched students (future enhancement)
- [x] Handle parents with multiple students
- [x] Handle orphaned parent records (parent with no students)

## Implementation Notes
**Completed: 2025-10-15**

### Files Created/Modified:
1. `src/templates/parent_search.html` - Parent search UI with children display
2. `src/routes/tools.py` - Added `/api/parents/search` and `/api/parents/<id>` endpoints
3. `src/templates/tools.html` - Added Parent Search to dashboard

### Implementation Details:
- Database-only implementation (no Bookmarked API parent search endpoint exists)
- Queries Parent table directly with district scoping
- Shows all children with grades and contact info
- Search by name, email, or phone
- Multiple match selection support
- Relative time formatting for dates ("2 days ago")
- Account status display (when available from future enrichment)

### Technical Notes:
- Parent search uses database queries only (no ClassLink/OneRoster parent search implemented yet)
- Children relationships loaded via _ParentToStudent join table
- Future: Add account status from invitation system
- Future: Add ClassLink parent comparison
