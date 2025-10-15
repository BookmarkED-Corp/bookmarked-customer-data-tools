# Secrets Management

This project uses a `secrets.yml` file for managing credentials, following the same pattern as the k8s-manifest secrets.

## Quick Start

1. **Copy the template**:
   ```bash
   cp secrets.yml.template secrets.yml
   ```

2. **Fill in your credentials** in `secrets.yml`

3. **Never commit** `secrets.yml` to git (it's already in `.gitignore`)

## Usage

The secrets can be accessed two ways:

### Option 1: Environment Variables (Highest Priority)

Set environment variables normally:
```bash
export STAGING_DB_PASSWORD="your-password"
python src/app.py
```

### Option 2: secrets.yml File

Use the SecretsManager in your code:

```python
from src.utils.secrets import get_secret, get_secret_int, get_secret_bool

# Get string secret
db_password = get_secret('STAGING_DB_PASSWORD')

# Get integer secret
port = get_secret_int('PORT', default=6001)

# Get boolean secret
debug = get_secret_bool('DEBUG', default=False)
```

## Priority Order

1. **Environment variables** (highest)
2. **secrets.yml file**
3. **Default value** (if provided)

This allows you to override secrets.yml values with environment variables when needed.

## Files

- `secrets.yml` - Your actual secrets (NEVER commit)
- `secrets.yml.template` - Template with placeholders (committed to git)
- `src/utils/secrets.py` - SecretsManager implementation

## Migration from .env

If you're currently using `.env`:

1. Values in `.env` will still work (via environment variables)
2. You can gradually move secrets to `secrets.yml`
3. Both systems work together harmoniously

## Security

- `secrets.yml` is gitignored
- Use restrictive file permissions: `chmod 600 secrets.yml`
- Never commit actual credentials
- For production, consider using AWS Secrets Manager

## Consistency with Other Projects

This follows the same pattern as:
- `k8s-manifest/Dev/secrets.yml`
- Other Bookmarked projects

Same format, same approach, easier to maintain!
