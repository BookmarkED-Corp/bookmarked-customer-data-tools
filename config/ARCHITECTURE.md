# Configuration System Architecture

## Overview

The machine-specific configuration system provides a flexible way to manage connection defaults across different developer environments.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     Developer's Machine                          │
│                                                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    Git Repository                          │  │
│  │                                                             │  │
│  │  config/defaults.json.template  (committed)                │  │
│  │  config/README.md               (committed)                │  │
│  │  CONFIGURATION.md               (committed)                │  │
│  │  .gitignore                     (committed)                │  │
│  └───────────────────────────────────────────────────────────┘  │
│                           │                                       │
│                           ▼                                       │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │             Local Config Files (gitignored)                │  │
│  │                                                             │  │
│  │  config/defaults.json        ← Machine-specific defaults   │  │
│  │  config/connections.config   ← Saved connections (enc)     │  │
│  │  config/.connection_key      ← Encryption key              │  │
│  └───────────────────────────────────────────────────────────┘  │
│                           │                                       │
│                           ▼                                       │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              Flask Application (Port 6001)                 │  │
│  │                                                             │  │
│  │  src/utils/connections.py                                  │  │
│  │    └─ ConnectionsConfig.load_defaults()                    │  │
│  │    └─ ConnectionsConfig.load_connections()                 │  │
│  │                                                             │  │
│  │  src/routes/connections.py                                 │  │
│  │    └─ GET /api/connections/defaults                        │  │
│  │    └─ GET /api/connections/load                            │  │
│  │    └─ POST /api/connections/save                           │  │
│  └───────────────────────────────────────────────────────────┘  │
│                           │                                       │
│                           ▼                                       │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              Browser (User Interface)                      │  │
│  │                                                             │  │
│  │  /connections/setup                                        │  │
│  │    1. Load defaults.json         (pre-fill)                │  │
│  │    2. Load connections.config    (override)                │  │
│  │    3. Display forms with values                            │  │
│  │    4. Test connections                                     │  │
│  │    5. Save connections                                     │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

### Page Load Sequence

```
1. Browser: GET /connections/setup
           ↓
2. Server: Render setup.html
           ↓
3. Browser: DOMContentLoaded event
           ↓
4. Browser: fetch('/api/connections/defaults')
           ↓
5. Server: ConnectionsConfig.load_defaults()
           ├─ Read config/defaults.json
           └─ Return JSON with defaults
           ↓
6. Browser: Pre-fill forms with defaults
           ↓
7. Browser: fetch('/api/connections/load')
           ↓
8. Server: ConnectionsConfig.load_connections()
           ├─ Read config/connections.config
           ├─ Decrypt sensitive fields
           ├─ Mask passwords/tokens with '****'
           └─ Return JSON with connections
           ↓
9. Browser: Override defaults with saved connections
           ↓
10. Browser: Display fully populated forms
```

### Save Sequence

```
1. User: Click "Save All Connections"
         ↓
2. Browser: Collect form values
         ↓
3. Browser: POST /api/connections/save
         ↓
4. Server: ConnectionsConfig.save_connections()
         ├─ Identify sensitive fields (password, token, api_key)
         ├─ Encrypt sensitive fields
         ├─ Add {field}_encrypted flags
         ├─ Write to config/connections.config
         └─ Set file permissions to 0600
         ↓
5. Server: Return success response
         ↓
6. Browser: Show success message
         ↓
7. Browser: Redirect to home page
```

## File Hierarchy

```
customer-data-tools/
├── config/
│   ├── README.md                    (committed) - Configuration docs
│   ├── ARCHITECTURE.md              (committed) - This file
│   ├── defaults.json.template       (committed) - Template with structure
│   ├── defaults.json                (gitignored) - Machine-specific defaults
│   ├── connections.config           (gitignored) - Saved connections (encrypted)
│   └── .connection_key              (gitignored) - Encryption key (auto-generated)
├── src/
│   ├── utils/
│   │   └── connections.py           - ConnectionsConfig class
│   ├── routes/
│   │   └── connections.py           - API endpoints
│   └── templates/
│       └── connections/
│           └── setup.html           - UI with JavaScript loader
├── .gitignore                       - Git exclusions
├── CONFIGURATION.md                 - User guide
└── IMPLEMENTATION_SUMMARY.md        - Implementation details
```

## Components

### 1. ConnectionsConfig Class

**Location**: `src/utils/connections.py`

**Methods**:
- `__init__(config_dir)` - Initialize with config directory
- `load_defaults()` - Load machine-specific defaults
- `load_connections()` - Load saved connections (decrypt)
- `save_connections(connections)` - Save connections (encrypt)
- `get_connection(type)` - Get specific connection
- `delete_connections()` - Delete saved connections

**Responsibilities**:
- File I/O for configuration files
- Encryption/decryption of sensitive data
- JSON parsing and validation

### 2. API Endpoints

**Location**: `src/routes/connections.py`

**Endpoints**:

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/connections/defaults` | Load machine-specific defaults |
| GET | `/api/connections/load` | Load saved connections |
| POST | `/api/connections/save` | Save connections |
| POST | `/api/connections/test/staging` | Test staging DB |
| POST | `/api/connections/test/production` | Test production DB |
| POST | `/api/connections/test/clickup` | Test ClickUp API |
| POST | `/api/connections/test/classlink` | Test ClassLink API |

### 3. Frontend UI

**Location**: `src/templates/connections/setup.html`

**JavaScript Functions**:
- `loadDefaults()` - Fetch and apply defaults
- `loadConnections()` - Fetch and apply saved connections
- `testConnection(type)` - Test specific connection
- `saveAllConnections()` - Save all form values

**Form Fields**:
- Staging DB: host, port, database, user, password
- Production DB: host, port, database, user, password
- HubSpot: access_token
- ClickUp: api_key
- ClassLink: api_key

## Security Model

### Encryption

```
┌─────────────────────────────────────────────────────────┐
│  Sensitive Field Detection                               │
│                                                           │
│  if field contains:                                      │
│    - "password"  → ENCRYPT                               │
│    - "token"     → ENCRYPT                               │
│    - "api_key"   → ENCRYPT                               │
│  else:                                                   │
│    - store plaintext                                     │
└─────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│  Encryption Process (Fernet)                             │
│                                                           │
│  1. Load key from .connection_key                        │
│  2. Create Fernet instance                               │
│  3. Encrypt field value                                  │
│  4. Store encrypted value                                │
│  5. Set {field}_encrypted = True flag                    │
└─────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│  Storage (connections.config)                            │
│                                                           │
│  {                                                        │
│    "staging": {                                          │
│      "host": "example.com",                              │
│      "password": "gAAAAABf...",  (encrypted)             │
│      "password_encrypted": true                          │
│    }                                                     │
│  }                                                       │
└─────────────────────────────────────────────────────────┘
```

### File Permissions

| File | Permissions | Reason |
|------|-------------|--------|
| `.connection_key` | 0600 (rw-------) | Contains encryption key |
| `connections.config` | 0600 (rw-------) | Contains encrypted data |
| `defaults.json` | 0644 (rw-r--r--) | User's local file |
| `defaults.json.template` | 0644 (rw-r--r--) | Template for copying |

### Git Protection

```
.gitignore patterns:

# Machine-specific connection defaults
config/defaults.json          ← Actual credentials
config/.connection_key        ← Encryption key
config/connections.config     ← Saved connections
```

## Loading Priority

```
Priority (Lower number = Higher priority)

1. Saved Connections (connections.config)
   ├─ User explicitly saved these
   ├─ Encrypted for security
   └─ Override defaults

2. Defaults (defaults.json)
   ├─ Machine-specific
   ├─ Developer's personal values
   └─ Used if no saved connections

3. Empty Fields
   └─ If neither defaults nor saved connections exist
```

## Use Cases

### Use Case 1: New Developer Onboarding

```
Step 1: Clone repository
  git clone <repo>
  cd customer-data-tools

Step 2: Copy template
  cd config
  cp defaults.json.template defaults.json

Step 3: Add credentials
  # Edit defaults.json with personal credentials

Step 4: Start app
  cd ..
  python src/app.py

Step 5: Visit setup page
  # http://localhost:6001/connections/setup
  # All fields pre-filled!

Step 6: Test and save
  # Click "Test Connection" buttons
  # Click "Save All Connections"

Result: Ready to work in < 5 minutes
```

### Use Case 2: Multiple Environments

```
Developer A (Staging-focused):
  defaults.json:
    staging: { host: "staging-db", password: "..." }
    production: { empty }

Developer B (Production-focused):
  defaults.json:
    staging: { empty }
    production: { host: "prod-db", password: "..." }

Result: No conflicts, different defaults per developer
```

### Use Case 3: API Key Management

```
Developer's defaults.json:
  {
    "clickup": { "api_key": "pk_12345..." },
    "classlink": { "api_key": "uuid..." }
  }

Result:
  - Keys pre-filled on every visit
  - No need to look up keys repeatedly
  - Keys stay local (never committed)
```

## Error Handling

### Missing defaults.json

```
Browser → GET /api/connections/defaults
Server → load_defaults()
       → defaults_file.exists() = False
       → Return { "success": False, "message": "No defaults file found" }
Browser → Skip pre-filling (show empty forms)
```

### Corrupt connections.config

```
Browser → GET /api/connections/load
Server → load_connections()
       → json.load() throws exception
       → Log error
       → Return None
Browser → Show empty forms or defaults only
```

### Invalid JSON

```
User → Manually edits defaults.json with invalid JSON
Server → load_defaults()
       → json.load() throws JSONDecodeError
       → Log error
       → Return None
Browser → Show empty forms
Solution: Validate JSON using `python -m json.tool`
```

## Performance Considerations

### File I/O

- Config files are small (< 1KB typically)
- Read operations are cached by OS
- No database queries required
- Fast load times (< 10ms)

### Encryption

- Fernet encryption is fast
- Only sensitive fields are encrypted
- Encryption happens on save (not read)
- Minimal performance impact

### Browser

- Two API calls on page load (defaults, connections)
- Async/await for non-blocking load
- Pre-filling happens in < 100ms
- No noticeable delay to user

## Testing Strategy

### Unit Tests

```python
# Test ConnectionsConfig class
def test_load_defaults():
    config = ConnectionsConfig()
    defaults = config.load_defaults()
    assert defaults is not None
    assert 'staging' in defaults

def test_save_and_load_connections():
    config = ConnectionsConfig()
    connections = {'staging': {'password': 'test'}}
    config.save_connections(connections)
    loaded = config.load_connections()
    assert loaded['staging']['password'] == 'test'
```

### Integration Tests

```python
# Test API endpoints
def test_defaults_endpoint(client):
    response = client.get('/api/connections/defaults')
    assert response.status_code == 200
    data = response.json
    assert data['success'] == True

def test_save_endpoint(client):
    data = {'staging': {'host': 'test', 'password': 'test'}}
    response = client.post('/api/connections/save', json=data)
    assert response.status_code == 200
```

### Manual Testing

```bash
# 1. Test defaults loading
curl http://localhost:6001/api/connections/defaults

# 2. Test connections loading
curl http://localhost:6001/api/connections/load

# 3. Test saving
curl -X POST http://localhost:6001/api/connections/save \
  -H "Content-Type: application/json" \
  -d '{"staging": {"host": "test"}}'
```

## Maintenance

### Adding New Connection Types

To add a new connection type (e.g., "github"):

1. Update `defaults.json.template`:
   ```json
   {
     "github": {
       "api_token": ""
     }
   }
   ```

2. Update `setup.html` with new form section

3. Update JavaScript to load/save new fields

4. Update encryption logic if needed

### Changing Encryption

To upgrade encryption algorithm:

1. Update `_encrypt()` and `_decrypt()` in `connections.py`
2. Migrate existing `connections.config` files
3. Update documentation

### Deprecating Old Format

To migrate from old format:

1. Create migration script
2. Read old format
3. Convert to new format
4. Write new files
5. Archive old files

## Troubleshooting

### Problem: Defaults not loading

**Debug Steps**:
```bash
# 1. Check if file exists
ls -la config/defaults.json

# 2. Validate JSON
cat config/defaults.json | python -m json.tool

# 3. Check browser console
# Open DevTools → Console → Look for errors

# 4. Check server logs
tail -f logs/app.log
```

### Problem: Encryption error

**Debug Steps**:
```bash
# 1. Check if key exists
ls -la config/.connection_key

# 2. Check permissions
stat config/.connection_key

# 3. Regenerate key
rm config/.connection_key config/connections.config
# Restart app (will regenerate)

# 4. Check Python cryptography module
pip show cryptography
```

### Problem: Gitignore not working

**Debug Steps**:
```bash
# 1. Check if already tracked
git ls-files config/defaults.json

# 2. Remove from tracking
git rm --cached config/defaults.json

# 3. Verify gitignore
git check-ignore -v config/defaults.json

# 4. Add and commit
git add .gitignore
git commit -m "Update gitignore"
```

## Future Enhancements

### 1. Validation Layer

```python
def validate_defaults(defaults: dict) -> tuple[bool, list[str]]:
    """Validate defaults structure and values"""
    errors = []

    # Check required keys
    for key in ['staging', 'production', 'clickup']:
        if key not in defaults:
            errors.append(f"Missing key: {key}")

    # Validate port numbers
    if defaults['staging'].get('port') > 65535:
        errors.append("Invalid port number")

    return len(errors) == 0, errors
```

### 2. Profile System

```json
{
  "profiles": {
    "staging": {
      "staging": { "host": "...", "password": "..." }
    },
    "production": {
      "production": { "host": "...", "password": "..." }
    }
  },
  "active_profile": "staging"
}
```

### 3. Import/Export

```python
def export_template(include_values=False):
    """Export defaults as template"""
    defaults = load_defaults()
    if not include_values:
        # Clear sensitive values
        defaults = clear_sensitive_fields(defaults)
    return json.dumps(defaults, indent=2)
```

### 4. UI Improvements

- "Reset to Defaults" button
- "Clear All" button
- "Import Configuration" button
- "Export Configuration" button
- Per-field "Reset" buttons

## Conclusion

The machine-specific configuration system provides a robust, secure, and developer-friendly way to manage connection defaults. The architecture is simple, maintainable, and extensible for future enhancements.
