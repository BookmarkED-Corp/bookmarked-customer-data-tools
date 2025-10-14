# Customer Data Tools

**Diagnose and resolve customer data issues in the Bookmarked platform**

A Flask-based web application that provides centralized tools for diagnosing customer integration issues, accessing source data from SIS systems, and comparing against Bookmarked production data.

**Target Launch:** October 31, 2025 (17 days)

## Features

- **Multi-Environment Support**: Access both staging and production environments
- **Customer Integration Management**: Store and manage integration settings for ClassLink, OneRoster, and custom sources
- **Diagnostic Tools**: Suite of tools for common customer data issues
- **HubSpot Integration**: Link diagnostic results directly to support tickets
- **Secure Credential Management**: Centralized, encrypted credential storage
- **AWS Deployment Ready**: Designed for serverless or container deployment

## Quick Start

### Prerequisites

- Python 3.9+
- PostgreSQL client libraries
- Access to Bookmarked staging/production databases (read-only)
- HubSpot API credentials (optional)

### Installation

1. **Clone and navigate to the project**
   ```bash
   cd /Users/ryan-bookmarked/platform/bookmarked/bookmarked-experimental/customer-data-tools
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

5. **Set up machine-specific connection defaults (optional but recommended)**
   ```bash
   cd config
   cp defaults.json.template defaults.json
   # Edit defaults.json with your connection defaults
   cd ..
   ```

   This step is optional but highly recommended. It allows you to save your default connection values (database credentials, API keys) that will automatically pre-fill the connection setup page. Each developer can have their own defaults without conflicts. See [CONFIGURATION.md](CONFIGURATION.md) for details.

6. **Initialize database connections**
   ```bash
   python scripts/test_connections.py
   ```

7. **Run the application**
   ```bash
   python src/app.py
   # Or: export FLASK_APP=src/app.py && flask run --port 6000
   ```

8. **Access the application**
   ```
   http://localhost:6001
   ```

## Project Structure

```
customer-data-tools/
├── docs/                           # Documentation
├── src/                            # Application source code
│   ├── app.py                      # Flask application entry point
│   ├── config/                     # Configuration management
│   ├── auth/                       # Authentication
│   ├── connectors/                 # Data source connectors
│   ├── tools/                      # Diagnostic tools
│   ├── models/                     # Data models
│   ├── routes/                     # Flask routes
│   ├── templates/                  # Jinja2 templates
│   └── static/                     # CSS, JS, images
├── customer-integration-settings/  # Customer configs (JSON)
├── tests/                          # Tests
├── scripts/                        # Utility scripts
├── kanban/                         # Kanban board for development
├── .env.example                    # Environment template
└── requirements.txt                # Python dependencies
```

## Documentation

- **[Project Requirements](PROJECT_REQUIREMENTS.md)** - Complete requirements specification
- **[Configuration Guide](CONFIGURATION.md)** - Machine-specific connection defaults
- **[Executive Summary](docs/EXECUTIVE_SUMMARY.html)** - Visual project overview
- **[Architecture](docs/ARCHITECTURE.md)** - System architecture and design decisions
- **[User Guide](docs/USER_GUIDE.md)** - How to use the diagnostic tools
- **[Deployment Guide](docs/DEPLOYMENT_GUIDE.md)** - AWS deployment instructions
- **[Claude Code Guide](CLAUDE.md)** - AI development workflow

## Diagnostic Tools

### Student Mismatch Resolver
Diagnose and resolve cases where incorrect students are assigned to parent accounts.

### Missing Data Finder
Identify missing students, classes, or enrollments by comparing source data with Bookmarked.

### Parent Email Conflict Detector
Find and resolve conflicts when multiple parents share the same email address.

### Campus Transfer Validator
Verify proper cleanup when students transfer between campuses.

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test
pytest tests/test_tools/test_student_mismatch.py
```

### Code Quality

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Lint
flake8 src/ tests/
```

### Kanban Board

View development tasks:
```bash
# Start Kanban server
node kanban_server.js

# Open in browser
open http://localhost:9001/kanban_ui.html
```

## Configuration

### Machine-Specific Connection Defaults

**NEW**: The application supports machine-specific connection defaults that automatically pre-fill the connection setup page.

```bash
cd config
cp defaults.json.template defaults.json
# Edit defaults.json with your credentials
```

Benefits:
- Each developer can have different defaults
- Credentials stay local (gitignored)
- Auto-fills forms on setup page
- Saves time and reduces errors

See **[CONFIGURATION.md](CONFIGURATION.md)** for complete documentation.

### Environment Variables

See `.env.example` for all configuration options. Key variables:

- `STAGING_DB_*`: Staging database credentials
- `PRODUCTION_DB_*`: Production database credentials (read-only)
- `CLASSLINK_API_KEY`: ClassLink API access
- `HUBSPOT_CLIENT_*`: HubSpot OAuth credentials

### Customer Integration Settings

Customer configurations are stored in `customer-integration-settings/` as JSON files:

```json
{
  "customer_id": "killeen-isd",
  "customer_name": "Killeen ISD",
  "integration_type": "OneRoster",
  "oneshelf_environment": "production",
  ...
}
```

See `customer-integration-settings/template.json` for full schema.

## Security

- All production database connections are READ-ONLY
- Credentials stored in AWS Secrets Manager (when deployed)
- HTTPS enforced in production
- Session timeout after inactivity
- Audit logging for all data access

## Deployment

### AWS Lambda (Recommended for low usage)

```bash
# Build deployment package
python scripts/build_lambda.py

# Deploy with SAM/Serverless Framework
sam deploy
```

### AWS ECS Fargate

```bash
# Build Docker image
docker build -t customer-data-tools .

# Push to ECR and deploy
aws ecr get-login-password | docker login --username AWS --password-stdin <ecr-url>
docker tag customer-data-tools:latest <ecr-url>/customer-data-tools:latest
docker push <ecr-url>/customer-data-tools:latest
```

See `docs/DEPLOYMENT_GUIDE.md` for detailed instructions.

## Support

### Common Issues

**Database connection fails:**
1. Verify credentials in `.env`
2. Check network connectivity
3. Ensure read-only user has correct permissions
4. Run `python scripts/test_connections.py`

**HubSpot OAuth not working:**
1. Verify callback URL matches HubSpot app settings
2. Check client ID and secret
3. Ensure redirect URI is accessible

**Tools return no data:**
1. Verify customer integration settings exist
2. Check source data credentials
3. Review logs: `tail -f logs/app.log`

## Contributing

This is an internal tool. For changes:

1. Create task in Kanban board
2. Implement feature/fix
3. Add tests
4. Update documentation
5. Submit for review

## License

Proprietary - Bookmarked, Inc.

---

**Version:** 1.0.0
**Last Updated:** 2025-10-14
**Status:** Active Development
