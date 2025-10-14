# Customer Integration Settings

This directory contains JSON configuration files for each customer's integration settings.

## Important Security Note

**DO NOT store credentials directly in these files!**

- Credentials should be stored in `.env` (local) or AWS Secrets Manager (production)
- These JSON files should only contain **references** to credentials
- Use `_ref` suffix for credential fields (e.g., `password_ref: "FTP_PASSWORD_KILLEEN"`)

## File Naming Convention

`<customer-id>.json`

Examples:
- `killeen-isd.json`
- `splendora-isd.json`
- `canyon-isd.json`

## Creating a New Customer Config

1. Copy `template.json`:
   ```bash
   cp template.json <customer-id>.json
   ```

2. Edit the file with customer-specific details

3. Add any new credentials to `.env`:
   ```bash
   FTP_PASSWORD_KILLEEN=secret_password_here
   ```

4. Test the configuration:
   ```bash
   python scripts/test_connections.py --customer <customer-id>
   ```

## Schema Reference

### Top Level Fields

- `customer_id` (string, required): Unique identifier (lowercase, hyphens)
- `customer_name` (string, required): Display name
- `district_name` (string, required): Full district name
- `integration_type` (string, required): "ClassLink", "OneRoster", or "Other"
- `oneshelf_environment` (string, required): "staging" or "production"
- `bookmarked_org_id` (string, required): Organization ID in Bookmarked database
- `active` (boolean, required): Is this integration currently active?

### ClassLink Configuration

```json
"classlink": {
  "enabled": true,
  "tenant_id": "string",
  "api_version": "v2",
  "notes": "Optional notes"
}
```

### OneRoster Configuration

```json
"oneroster": {
  "enabled": true,
  "api_url": "https://...",
  "version": "1.1" or "1.2",
  "client_id_ref": "ENV_VAR_NAME",
  "client_secret_ref": "ENV_VAR_NAME",
  "csv_upload_enabled": true
}
```

### FTP Configuration

```json
"ftp": {
  "enabled": true,
  "host": "ftp.example.com",
  "port": 21,
  "username_ref": "ENV_VAR_NAME",
  "password_ref": "ENV_VAR_NAME",
  "remote_path": "/path/to/files",
  "file_pattern": "*.csv"
}
```

## Example: Killeen ISD

From the requirements, Killeen ISD uses OneRoster. Here's an example config:

```json
{
  "customer_id": "killeen-isd",
  "customer_name": "Killeen ISD",
  "district_name": "Killeen Independent School District",
  "integration_type": "OneRoster",

  "classlink": {
    "enabled": false
  },

  "oneroster": {
    "enabled": true,
    "api_url": "https://killeen.oneroster.com/v1p2",
    "version": "1.2",
    "client_id_ref": "ONEROSTER_KILLEEN_CLIENT_ID",
    "client_secret_ref": "ONEROSTER_KILLEEN_CLIENT_SECRET",
    "csv_upload_enabled": true
  },

  "ftp": {
    "enabled": false
  },

  "oneshelf_environment": "production",
  "bookmarked_org_id": "789",
  "active": true,

  "contact_info": {
    "technical_contact": "it@killeenisd.org",
    "support_contact": "support@bookmarked.com"
  },

  "notes": "High priority district with active parent portal usage"
}
```

## Maintenance

### Adding a New Integration Type

1. Update `template.json` with new section
2. Update this README with schema documentation
3. Update `src/models/customer.py` to parse new type
4. Create new connector in `src/connectors/`

### Deprecating a Customer

Set `"active": false` instead of deleting the file. This preserves historical configuration.

### Bulk Updates

```bash
# Update all configs at once (be careful!)
python scripts/bulk_update_customers.py --field "api_version" --value "v2"
```

## Git Workflow

**These files ARE committed to git** (unlike `.env`), because:
- They don't contain actual credentials
- They're needed for deployment
- Changes should be tracked

However, **always review before committing** to ensure no secrets leaked in.
