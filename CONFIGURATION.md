# Machine-Specific Configuration System

## Overview

The customer-data-tools application now supports machine-specific configuration defaults. This allows each developer to maintain their own default connection values that automatically populate the connection setup page.

## Features

- **Machine-Specific**: Each developer can have different defaults on their machine
- **Gitignored**: Your credentials stay local and are never committed to git
- **Auto-Load**: Defaults automatically pre-fill the connection setup forms
- **Override-Friendly**: Saved connections override defaults
- **Secure**: Saved connections use encryption for sensitive data

## Quick Start

### 1. Create Your Defaults File

```bash
cd config
cp defaults.json.template defaults.json
```

### 2. Edit Your Defaults

Open `config/defaults.json` and add your connection defaults:

```json
{
  "staging": {
    "host": "your-staging-db-host",
    "port": 5432,
    "database": "your-database",
    "user": "your-username",
    "password": "your-password"
  },
  "clickup": {
    "api_key": "your-clickup-api-key"
  },
  "classlink": {
    "api_key": "your-classlink-api-key"
  }
}
```

### 3. Start the Application

```bash
python src/app.py
```

### 4. Visit the Setup Page

Navigate to `http://localhost:6001/connections/setup`

Your defaults will automatically pre-fill the forms!

## How It Works

### Loading Priority

When you visit the connections setup page, values are loaded in this order:

1. **Defaults** from `config/defaults.json` (if it exists)
2. **Saved Connections** from `config/connections.config` (if they exist)

Saved connections always override defaults.

### Saving Connections

When you click "Save All Connections":

- Values are saved to `config/connections.config`
- Passwords, tokens, and API keys are automatically encrypted
- The encryption key is stored in `config/.connection_key`
- Next time you load the page, these saved values are used

### File Descriptions

| File | Purpose | Git Status |
|------|---------|------------|
| `config/defaults.json.template` | Template showing structure | Committed |
| `config/defaults.json` | Your machine-specific defaults | Gitignored |
| `config/connections.config` | Saved connections (encrypted) | Gitignored |
| `config/.connection_key` | Encryption key | Gitignored |
| `config/README.md` | Configuration documentation | Committed |

## Use Cases

### Scenario 1: New Developer Setup

```bash
# Clone the repo
git clone <repo>
cd customer-data-tools

# Set up your defaults
cd config
cp defaults.json.template defaults.json
# Edit defaults.json with your credentials

# Start working!
cd ..
python src/app.py
```

### Scenario 2: Multiple Environments

Developer A works primarily with staging:
```json
{
  "staging": {
    "host": "staging-db.example.com",
    "password": "staging-password"
  }
}
```

Developer B works primarily with production:
```json
{
  "production": {
    "host": "prod-db.example.com",
    "password": "prod-password"
  }
}
```

Both developers can work on the same codebase without conflicts!

### Scenario 3: API Key Management

Store your frequently-used API keys:
```json
{
  "clickup": {
    "api_key": "pk_12345_YOUR_KEY"
  },
  "classlink": {
    "api_key": "your-uuid-key"
  }
}
```

They'll be pre-filled every time you visit the setup page.

## Security Best Practices

1. **Never commit** `config/defaults.json` - it contains credentials
2. **Never commit** `config/connections.config` - it contains encrypted data
3. **Never commit** `config/.connection_key` - it's the encryption key
4. **Use read-only credentials** when possible for database connections
5. **Rotate API keys** regularly and update your defaults file

## Troubleshooting

### Problem: Defaults Not Loading

**Solution**: Check if `config/defaults.json` exists and is valid JSON
```bash
cd config
cat defaults.json | python -m json.tool
```

### Problem: Saved Connections Not Loading

**Solution**: Check if `config/connections.config` and `config/.connection_key` exist
```bash
ls -la config/
```

### Problem: Encryption Error

**Solution**: Delete the encryption key and saved connections (they'll be regenerated)
```bash
rm config/.connection_key config/connections.config
# Then save your connections again from the UI
```

### Problem: Wrong Defaults Showing

**Solution**: Remember that saved connections override defaults. Check both files:
```bash
# View defaults (plain JSON)
cat config/defaults.json

# View saved connections (encrypted)
cat config/connections.config
```

## API Endpoints

The system adds a new endpoint:

- `GET /api/connections/defaults` - Load machine-specific defaults

Existing endpoints:
- `GET /api/connections/load` - Load saved connections (encrypted)
- `POST /api/connections/save` - Save connections (encrypts sensitive data)

## Migration from .env

If you're currently using `.env` for connection values:

1. The `.env` file is still supported for application-level config
2. Copy your connection values from `.env` to `config/defaults.json`
3. The defaults system is additive - it doesn't replace `.env`
4. Use `.env` for app-wide settings, `defaults.json` for personal connection defaults

## Example defaults.json

```json
{
  "staging": {
    "host": "bookmarked-stage-db-cluster.cluster-ct7orinaenkn.us-east-1.rds.amazonaws.com",
    "port": 5432,
    "database": "prod_dump_0925",
    "user": "postgres",
    "password": "your-password-here"
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
    "api_key": "pk_81574061_YOUR_KEY_HERE"
  },
  "classlink": {
    "api_key": "your-uuid-key-here"
  }
}
```

## Benefits

1. **Faster Setup**: Pre-filled forms save time
2. **No Conflicts**: Each developer has their own defaults
3. **Secure**: Credentials never committed to git
4. **Flexible**: Override defaults anytime by saving new connections
5. **Simple**: Just copy a template and fill in values

## Questions?

See `config/README.md` for more details on the configuration system.
