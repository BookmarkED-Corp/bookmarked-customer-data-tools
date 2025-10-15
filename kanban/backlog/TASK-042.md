---
id: TASK-042
title: District Selection and ClassLink Data Validation
type: feature
priority: high
assignee: agent
phase: 2
estimated_hours: 6
---

## Description
Implement district selection workflow that allows users to choose a district from Staging or Production environment, then validates if ClassLink historical data exists for that district. The selected environment and district should persist across sessions.

## Acceptance Criteria
- [ ] Query Districts from Staging or Production API (user selectable)
- [ ] Display districts in searchable dropdown/list
- [ ] User selection persists in session
- [ ] Environment selection (Staging/Production) persists
- [ ] Query `ClasslinkDistrict` table for historical data
- [ ] Display validation badge: "Historical ClassLink data found ✓" or "NOT FOUND ✗"
- [ ] Show district metadata (name, ID, last sync date if available)
- [ ] "Use Cases" section becomes enabled after district selection
- [ ] Clear visual feedback during data loading
- [ ] Handle errors gracefully (API down, no districts found, etc.)

## Technical Details

### API/Database Query
```sql
-- Check for ClassLink historical data
SELECT
    cd.id,
    cd."sourcedId",
    cd.name,
    cd."lastSync",
    cd."districtId"
FROM "ClasslinkDistrict" cd
WHERE cd."districtId" = :selected_district_id;
```

### Data Sources
- **Districts List**: Query from `District` table or API endpoint
- **ClassLink Validation**: Query `ClasslinkDistrict` table
- **Environment**: User selects Staging or Production

### UI Components
1. **Environment Selector**: Radio buttons or toggle (Staging / Production)
2. **District Dropdown**: Searchable select with district names
3. **Validation Badge**: Visual indicator for ClassLink data availability
4. **District Info Panel**: Show selected district details
5. **Use Cases Menu**: Enabled after district selection

### Persistence
- Store in session:
  - `selected_environment` (staging/production)
  - `selected_district_id`
  - `selected_district_name`
  - `has_classlink_data` (boolean)

## UI Flow
1. User selects Environment (Staging or Production)
2. App queries Districts from selected environment
3. User selects District from dropdown
4. App queries ClasslinkDistrict table for validation
5. Display validation result with badge
6. Enable "General Tools" section
7. Persist selection for session

## Dependencies
- TASK-041 (Settings configuration must be complete)
- Database connector with read access
- API connector (if using API instead of direct DB)

## Notes
- Initially query District table directly from database
- Consider adding API endpoint for districts list (future enhancement)
- Show last sync date if ClassLink data exists
- Provide helpful message if no ClassLink data found
- Consider caching district list for performance
