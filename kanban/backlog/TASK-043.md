---
id: TASK-043
title: General Tools - Find Student and Side-by-Side Compare
type: feature
priority: high
assignee: agent
phase: 2
estimated_hours: 10
---

## Description
Implement the first diagnostic tool: Find Student in both Bookmarked Database and ClassLink, then display side-by-side comparison of student data from both systems. This serves as the foundation for all future diagnostic tools.

## Acceptance Criteria
- [ ] "Find Student" tool accessible from General Tools menu
- [ ] Search by: Student ID, Name, Email, or sourcedId
- [ ] Query Bookmarked database for student in selected district
- [ ] Query ClassLink API for same student in selected district/tenant
- [ ] Display side-by-side comparison table
- [ ] Highlight differences between systems (different values, missing fields)
- [ ] Show all relevant student fields (name, email, grade, sourcedId, etc.)
- [ ] Handle cases where student exists in only one system
- [ ] Display enrollment/class information from both systems
- [ ] Display campus assignment from both systems
- [ ] Export comparison results (CSV or PDF)
- [ ] Clear visual indicators for data mismatches

## Technical Details

### Search Implementation
```python
# Bookmarked Database Query
SELECT
    s.id,
    s."sourcedId",
    s."givenName",
    s."familyName",
    s.email,
    s.grade,
    c.name as campus_name
FROM "Student" s
LEFT JOIN "_CampusToStudent" cs ON s.id = cs."B"
LEFT JOIN "Campus" c ON cs."A" = c.id
WHERE c."districtId" = :district_id
    AND (
        s."sourcedId" = :search_term
        OR s."givenName" ILIKE :search_term
        OR s."familyName" ILIKE :search_term
        OR s.email ILIKE :search_term
    )
```

### ClassLink API Query
```python
# GET /v2/students/:id
# Or search: GET /v2/students?filter=sourcedId eq '123456'
```

### Comparison Fields
- **Basic Info**: sourcedId, givenName, familyName, email
- **Demographics**: grade, birthDate, gender
- **Status**: status, enabledUser
- **Location**: campus/school assignment
- **Enrollment**: classes/courses enrolled
- **Metadata**: lastModified, created dates

### UI Layout
```
┌─────────────────────────────────────────────────────────┐
│  Search Student                                         │
│  [Search by ID/Name/Email] [Search Button]             │
└─────────────────────────────────────────────────────────┘

┌─────────────────────┬─────────────────────────────────┐
│ Bookmarked Database │ ClassLink API                   │
├─────────────────────┼─────────────────────────────────┤
│ sourcedId: 314461   │ sourcedId: 314461               │
│ Name: John Doe      │ Name: John Doe                  │
│ Email: jdoe@...     │ Email: jdoe@...                 │
│ Grade: 5            │ Grade: 5 ✓                      │
│ Campus: Peebles     │ Campus: NOT FOUND ✗             │
│ Status: Active      │ Status: active                  │
└─────────────────────┴─────────────────────────────────┘

[Export Results] [Search Another Student]
```

### Difference Highlighting
- **Green ✓**: Values match
- **Red ✗**: Values differ or missing
- **Yellow ⚠**: Potential issue (format mismatch, etc.)

## Use Cases Supported
1. **Student exists in both systems** - Show side-by-side comparison
2. **Student only in Bookmarked** - Highlight missing from ClassLink
3. **Student only in ClassLink** - Highlight missing from Bookmarked
4. **Data mismatch** - Highlight specific field differences
5. **Campus transfer** - Show if student moved campuses

## Dependencies
- TASK-042 (District selection must be complete)
- BookmarkedDBConnector with student queries
- ClassLinkConnector with student search
- Session management for selected district

## Notes
- This is the foundation tool - keep it simple and extensible
- Use this pattern for future diagnostic tools
- Consider pagination for multiple search results
- Add detailed logging for troubleshooting
- Performance: Cache ClassLink responses for 5 minutes
- Future: Add "Fix" buttons to resolve discrepancies
