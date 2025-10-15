---
id: TASK-041
title: Complete Settings Configuration and Persistence
type: feature
priority: critical
assignee: agent
phase: 2
estimated_hours: 8
---

## Description
Implement comprehensive settings configuration UI and persistence layer for all data integrations. Users should be able to configure and test connections to Staging API, Production API, Staging Database, Production Database, and ClassLink API. All settings should persist and be validated before proceeding to diagnostic tools.

## Acceptance Criteria
- [ ] Add Staging API settings to defaults (from infrastructure)
- [ ] Add Production API settings to defaults (from infrastructure)
- [ ] Staging Database connection configured and tested
- [ ] Production Database connection configured and tested
- [ ] ClassLink API Key configuration with district/tenant validation
- [ ] Test button for each integration validates against real tenant from database
- [ ] All connections validated before allowing access to next screen
- [ ] Settings screen accessible from main navigation (return to settings)
- [ ] Support for ClassLink integration (OneRoster FTP support planned for future)
- [ ] Connection state persisted in config/connections.config (encrypted)
- [ ] Visual indicators for connection status (✓ connected, ✗ failed, ⚠ not configured)

## Technical Details

### API Configuration
- Staging API: `https://stg.api.bookmarked.com`
- Production API: `https://prod.api.bookmarked.com`
- Load from infrastructure defaults

### Database Configuration
- Staging DB: bookmarked-stage-db-cluster.cluster-ct7orinaenkn.us-east-1.rds.amazonaws.com
- Production DB: bookmarked-prod-db.cqqw6jilbuwg.us-east-1.rds.amazonaws.com
- Use DATABASE_ACCESS.md as reference

### ClassLink Configuration
- API URL: `https://api.classlink.com/v2`
- Test with real district tenant from `ClasslinkDistrict` table
- Validate by fetching district info

### UI Flow
1. Display all connection settings with test buttons
2. Test each connection and show results
3. Enable "Continue to Tools" button only when all required connections are valid
4. Persist all settings for future sessions
5. Add "Back to Settings" link in main navigation

## Dependencies
- Connection management system (completed)
- Database connector (completed)
- ClassLink connector (completed)
- config/defaults.json (updated)

## Notes
- Start with ClassLink only; OneRoster FTP will be added later
- Connections must be testable without leaving settings page
- Settings should survive app restarts
- Add helpful error messages for connection failures
- Consider read-only vs read-write access for databases
