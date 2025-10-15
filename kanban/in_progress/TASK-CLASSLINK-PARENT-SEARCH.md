---
id: TASK-CLASSLINK-PARENT-SEARCH
title: Implement progressive ClassLink parent search with caching
type: feature
priority: high
assignee: claude
parent_task: TASK-SEARCH-PARENT
phase: 2
estimated_hours: 6
status: in_progress
started_date: 2025-10-15
---

## Description
Implement a progressive search strategy for finding parents in ClassLink with live API data, browser caching, and user-controlled deep search option.

## Problem
Current parent search only queries the Bookmarked database (cached data from last sync). Need live ClassLink data with intelligent search strategy to balance speed vs completeness.

## Solution
Three-level progressive search:
1. **Database lookup** - Get parent metadata (sourcedId, email) - 0.1s
2. **Targeted ClassLink search** - Use metadata to search live API (paginated, early exit) - 1-2s
3. **Deep search** (user opt-in) - Fetch all ~1890 users from ClassLink with progress - 6s initial, then <0.1s from cache

## Features
### Backend API Endpoints
- [x] `/api/parents/search` - Database search (already exists)
- [ ] `/api/classlink/parent/targeted-search` - Paginated ClassLink search
- [ ] `/api/classlink/users/bulk` - Bulk user fetching for deep search

### Frontend Components
- [ ] Cache management (sessionStorage, 15 min TTL)
- [ ] Loading spinner overlay ("🔄 Searching ClassLink...")
- [ ] Progress bar for deep search ("Loading users from ClassLink (1200/1890)...")
- [ ] Deep search confirmation modal
- [ ] Progressive search flow implementation

### Search Flow
```
User searches → DB lookup (get metadata)
              ↓
         Targeted ClassLink search (use sourcedId/email)
              ↓ Not found
         Show prompt: "Fetch all users? (6 seconds)"
              ↓ User confirms
         Deep search with progress bar
              ↓
         Cache in sessionStorage for 15 min
              ↓
         Future searches use cache (<0.1s)
```

## Technical Details

### Backend Endpoints

#### 1. `/api/classlink/parent/targeted-search`
```python
POST /api/classlink/parent/targeted-search
Body: {
  "search_term": "email or name",
  "district_id": 6,
  "environment": "staging",
  "parent_sourcedId": "Guardian_15649"  # Optional, from DB lookup
}

Response: {
  "success": true,
  "parent": {...},  # Found parent
  "checked": 500,    # Records searched
  "total_estimated": 1890
}
```

#### 2. `/api/classlink/users/bulk`
```python
POST /api/classlink/users/bulk
Body: {
  "district_id": 6,
  "environment": "staging",
  "offset": 0,
  "limit": 500
}

Response: {
  "success": true,
  "users": [...],     # 500 users
  "has_more": true,
  "offset": 0,
  "total_fetched": 500,
  "progress": 26      # Percentage
}
```

### Frontend Cache Structure
```javascript
// sessionStorage keys
const CACHE_KEY = `classlink_users_district_${districtId}`;
const CACHE_TIMESTAMP_KEY = `classlink_users_timestamp_district_${districtId}`;
const CACHE_TTL = 15 * 60 * 1000; // 15 minutes

// Cache format
{
  users: [...],      // All users
  timestamp: 1234567890,
  district_id: 6,
  total_count: 1890
}
```

## Acceptance Criteria
- [ ] Database lookup returns parent metadata (sourcedId, email)
- [ ] Targeted search finds parent in ~1-2 seconds using metadata
- [ ] Deep search shows progress bar and updates in real-time
- [ ] Deep search prompts user before starting
- [ ] Cache persists for 15 minutes in sessionStorage
- [ ] Subsequent searches use cache (<0.1s response)
- [ ] Cache indicator shows when using cached data
- [ ] All searches return live ClassLink data (no stale data)
- [ ] Loading spinners show during all API calls
- [ ] Error handling for all failure scenarios

## Implementation Notes

### Phase 1: Backend (CURRENT)
- [ ] Add helper function to get ClassLink config for district
- [ ] Implement targeted search endpoint
- [ ] Implement bulk users endpoint
- [ ] Test endpoints with Splendora ISD (district 6)

### Phase 2: Frontend
- [ ] Add cache management functions
- [ ] Add spinner/progress UI components
- [ ] Implement progressive search flow
- [ ] Add deep search modal
- [ ] Wire up new endpoints
- [ ] Test complete flow

### Phase 3: Testing & Polish
- [ ] Test with real parent: sherribessire@yahoo.com
- [ ] Test cache expiration
- [ ] Test error scenarios
- [ ] Performance validation
- [ ] Update documentation

## Known Issues / Limitations
- ClassLink doesn't support direct email search (must fetch and filter)
- Role filter `role='guardian'` has pagination limit of 1000 (misses 890 guardians)
- Best approach: Fetch all users without role filter (2000 limit works)
- Guardian_15649 found at position 1200+ (requires high limit or deep search)

## Related Files
- `src/routes/tools.py` - Backend endpoints
- `src/templates/parent_search.html` - Frontend UI
- `src/connectors/classlink.py` - ClassLink API client
- `benchmark_parent_search.py` - Performance tests
- `find_parent_comprehensive.py` - Search method tests

## Performance Benchmarks
- Database query: 0.05-0.1s
- Targeted search: 1-2s (500 records/request)
- Deep search (first time): ~6s (fetches 2000 users)
- Deep search (cached): <0.1s (sessionStorage lookup)

## Dependencies
- ClassLink API key (configured)
- OneRoster Application ID for district
- Database connection (for metadata lookup)

## Testing Checklist
- [ ] Test with known parent (sherribessire@yahoo.com)
- [ ] Test with unknown parent
- [ ] Test cache creation
- [ ] Test cache usage
- [ ] Test cache expiration (15 min)
- [ ] Test multiple districts (separate caches)
- [ ] Test error handling
- [ ] Test progress bar updates
- [ ] Test modal confirmation

## Documentation Updates Needed
- [ ] Update API reference with new endpoints
- [ ] Update user guide with search strategy
- [ ] Add caching documentation
- [ ] Add performance notes

---

**Status**: In Progress
**Next Steps**:
1. Complete backend endpoint implementation
2. Test endpoints with curl/Postman
3. Begin frontend integration
