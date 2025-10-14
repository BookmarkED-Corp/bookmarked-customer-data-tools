# Configuration Directory

This directory contains machine-specific configuration files for the customer-data-tools application.

## Files

### defaults.json (gitignored)
Machine-specific default connection values. Each developer can have different defaults that automatically populate the connection setup page.

**Structure:**
```json
{
  "staging": {
    "host": "database-hostname",
    "port": 5432,
    "database": "database-name",
    "user": "username",
    "password": "password"
  },
  "production": {
    "host": "",
    "port": 5432,
    "database": "",
    "user": "",
    "password": ""
  },
  "hubspot": {
    "access_token": ""
  },
  "clickup": {
    "api_key": ""
  },
  "classlink": {
    "api_key": ""
  }
}
```

**Setup:**
1. Copy `defaults.json.template` to `defaults.json`
2. Fill in your connection defaults
3. The file is gitignored - your credentials stay local

### defaults.json.template (committed to git)
Template showing the structure of defaults.json. Contains empty values.

### connections.config (gitignored)
Saved connection configurations with encrypted sensitive data. Auto-generated when you save connections from the UI.

### .connection_key (gitignored)
Encryption key for connections.config. Auto-generated on first use.

## How It Works

1. **Page Load**: When you visit `/connections/setup`, the page loads:
   - First: Defaults from `defaults.json` (if it exists)
   - Then: Saved connections from `connections.config` (if they exist)
   - Saved connections override defaults

2. **Saving**: When you click "Save All Connections":
   - Values are saved to `connections.config`
   - Passwords, tokens, and API keys are encrypted
   - Next time you load the page, these saved values are used

3. **Defaults**: The `defaults.json` file provides:
   - Quick setup for new developers
   - Common values you use frequently
   - No need to re-enter credentials each time

## Security

- All files in this directory (except templates and README) are gitignored
- Passwords and API keys are encrypted when saved to `connections.config`
- The encryption key is stored in `.connection_key` with restrictive permissions (0600)
- Never commit `defaults.json`, `connections.config`, or `.connection_key` to git

## Example Workflow

```bash
# First time setup
cd config
cp defaults.json.template defaults.json
# Edit defaults.json with your credentials

# Start the app
cd ..
python src/app.py

# Visit http://localhost:6001/connections/setup
# Your defaults will be pre-filled!
# Test connections and save them
```

## Per-Developer Configuration

Each developer can have different defaults:

**Developer A (Ryan)**
- Defaults to staging database
- Has ClickUp and ClassLink API keys pre-filled

**Developer B**
- Defaults to production database
- Has HubSpot credentials pre-filled

Both can work on the same codebase without conflicts!
