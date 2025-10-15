---
id: TASK-DIAGNOSTIC-SEARCH
title: Build diagnostic search tool with side-by-side data comparison
type: feature
priority: high
assignee: unassigned
phase: 2
estimated_hours: 12
---

## Description
Create a comprehensive search tool in the web app that allows support engineers to search for students, parents, and teachers, then compare source data (ClassLink/OneRoster) with Bookmarked API data side-by-side. This tool helps diagnose whether data issues originate from the source system or Bookmarked.

## User Workflow
1. **Select District/Tenant**: Choose from list of districts via Bookmarked API
2. **Search**: Search for students, parents, or teachers by name, email, or ID
3. **View Comparison**: See side-by-side comparison of:
   - **Left side**: Source data (ClassLink API or OneRoster file)
   - **Right side**: Bookmarked API data
4. **Historical View**: For ClassLink, show historical changes from snapshot database

## Components to Build

### 1. District Selection UI
- Dropdown or autocomplete to select district
- Load districts from Bookmarked API (`/districts`)
- Store selected district in session

### 2. Search Interface
- Tabs for: Students | Parents | Teachers
- Search inputs: Name, Email, External ID
- Search both source and Bookmarked simultaneously

### 3. Side-by-Side Comparison View
**Left Column: Source Data (ClassLink/OneRoster)**
- Student: demographics, external ID, grade, school
- Enrollments: classes, teachers, schedules
- School: name, district, type
- Parent relationships (if applicable)

**Right Column: Bookmarked API Data**
- Equivalent student record from OneShelf API
- Enrollments and class assignments
- School and campus info
- Parent-student relationships

**Diff Highlighting**:
- Green: Data matches
- Red: Data mismatch or missing
- Yellow: Data exists in only one source

### 4. Historical Changes (ClassLink only)
- Query ClassLink snapshot database for historical records
- Show timeline of changes to the student record
- Display what changed, when, and delta

## Data Sources

### Source Data
1. **ClassLink API**:
   - OAuth2 authenticated requests
   - OneRoster 1.1/1.2 endpoints
   - Real-time data from district SIS

2. **OneRoster File**:
   - CSV files uploaded by district
   - Parse manifest and relevant CSVs
   - Static snapshot data

3. **ClassLink Snapshot DB**:
   - Database: `classlink_snapshots` (check bookmarked-back for schema)
   - Historical records with timestamps
   - Track changes over time

### Bookmarked Data
- **OneShelf API** (via JWT authentication)
- Endpoints:
  - `/students/{id}`
  - `/students/search?q={term}`
  - `/enrollments?student_id={id}`
  - `/parents?student_id={id}`
  - `/teachers/{id}`
  - `/classes/{id}`

## Sub-Tasks
- [TASK-SEARCH-STUDENT] Student search with enrollments and schools
- [TASK-SEARCH-PARENT] Parent search with related students
- [TASK-SEARCH-TEACHER] Teacher search with classes and schools

## Technical Requirements

### Backend Routes
- `GET /tools/search` - Main search page
- `POST /api/search/students` - Search students in both sources
- `POST /api/search/parents` - Search parents in both sources
- `POST /api/search/teachers` - Search teachers in both sources
- `GET /api/comparison/{type}/{id}` - Get detailed comparison data
- `GET /api/history/classlink/{id}` - Get ClassLink historical data

### Database Queries
- Read ClassLink snapshot tables (see bookmarked-back schema)
- Query historical records with timestamps
- Join student, enrollment, school tables

### API Integration
- ClassLink OAuth2 connector (already implemented)
- OneRoster file parser
- Bookmarked API connector (JWT auth - already implemented)

## Acceptance Criteria
- [ ] User can select a district from Bookmarked API
- [ ] User can search for students, parents, teachers
- [ ] Results show side-by-side comparison of source vs Bookmarked data
- [ ] Data differences are clearly highlighted (match/mismatch/missing)
- [ ] For ClassLink integrations, historical changes are displayed
- [ ] For OneRoster files, data is parsed from CSV uploads
- [ ] Performance: Search completes in < 5 seconds
- [ ] Error handling: Clear messages when data source unavailable
- [ ] Responsive UI: Works on desktop and tablet

## Data Model Understanding Required

### Review These Codebases
1. **bookmarked-back**:
   - Student, Parent, Teacher models
   - Enrollment, Class, School relationships
   - Database schema and foreign keys
   - ClassLink snapshot tables

2. **SIS Integration System**:
   - ClassLink OneRoster format documentation
   - OneRoster CSV structure and relationships
   - Data transformation logic
   - Validation rules

### Key Relationships to Map
- Student → School (enrollment)
- Student → Classes (enrollments)
- Student → Parents (family relationships)
- Teacher → Classes
- Teacher → Schools
- Class → School

## UI Mockup Concept
```
┌─────────────────────────────────────────────────────────┐
│ Diagnostic Search Tool                                  │
├─────────────────────────────────────────────────────────┤
│ District: [Killeen ISD ▼]                               │
│ Search:   [🔍 John Smith____________] [Search Students] │
│ Tabs:     [Students] Parents  Teachers                  │
├──────────────────────────┬──────────────────────────────┤
│ ClassLink Source         │ Bookmarked API               │
├──────────────────────────┼──────────────────────────────┤
│ Name: Smith, John        │ Name: Smith, John        ✓   │
│ Grade: 9                 │ Grade: 9                 ✓   │
│ Email: john@killeen.edu  │ Email: john@killeen.edu  ✓   │
│ School: Killeen HS       │ School: Killeen HS       ✓   │
│ External ID: 123456      │ External ID: 123456      ✓   │
│                          │                              │
│ Enrollments:             │ Enrollments:                 │
│ - Math 101 (Period 1)    │ - Math 101 (Period 1)    ✓   │
│ - English 9 (Period 2)   │ ❌ MISSING                  │
│                          │                              │
│ [View History]           │ [Sync Now]                   │
└──────────────────────────┴──────────────────────────────┘
```

## Dependencies
- JWT authentication (TASK-API-JWT-AUTH) ✅ COMPLETE
- ClassLink OAuth2 connector
- Bookmarked database access (read-only)

## Notes
- This is a PRIMARY diagnostic tool for support team
- Will be used daily to troubleshoot customer data issues
- Must handle large districts (10k+ students)
- Consider caching search results for performance
- Add export functionality (CSV/JSON) in future iteration
