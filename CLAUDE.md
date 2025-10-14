# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Customer Data Tools** is a Flask-based web application for diagnosing and resolving customer data issues in the Bookmarked platform. The system connects to multiple data sources (SIS systems, Bookmarked APIs, HubSpot) to help support engineers quickly identify and resolve data discrepancies.

**Key Features:**
- Diagnostic tools for common customer data issues
- Multi-environment support (staging/production)
- Customer integration settings management
- HubSpot ticket integration
- Secure credential management
- AWS deployment ready (Lambda or ECS Fargate)

## Architecture

### Application Flow

```
User Authentication
  ↓
Tool Selection (or HubSpot Ticket Import)
  ↓
Data Gathering:
  - Customer Integration Settings
  - Source Data (ClassLink/OneRoster/FTP)
  - Bookmarked Data (API or Direct DB)
  ↓
Data Comparison & Analysis
  ↓
Results Display
  ↓
Optional: Update HubSpot Ticket
```

### Component Structure

**Connectors** (`src/connectors/`):
- `bookmarked_api.py` - Bookmarked REST API client
- `bookmarked_db.py` - Direct PostgreSQL queries (read-only)
- `classlink.py` - ClassLink OAuth2 and API integration
- `oneroster.py` - OneRoster API and CSV parsing
- `hubspot.py` - HubSpot API for tickets
- `ftp_client.py` - FTP server access for customer data

**Tools** (`src/tools/`):
- `base_tool.py` - Abstract base class for all diagnostic tools
- `student_mismatch.py` - Student assignment issues
- `missing_data.py` - Missing students/classes/enrollments
- `parent_conflicts.py` - Parent email conflicts
- `campus_transfer.py` - Campus transfer validation

**Models** (`src/models/`):
- `customer.py` - Customer integration settings
- `diagnostic_result.py` - Diagnostic run results
- `user.py` - Application users

**Routes** (`src/routes/`):
- `dashboard.py` - Main dashboard
- `tools.py` - Diagnostic tool routes
- `settings.py` - Settings and credential management
- `hubspot.py` - HubSpot integration routes

## Configuration

### Environment Files

- **`.env`** - Local development (gitignored)
- **`.env.example`** - Template with all variables documented

### Customer Integration Settings

Stored in `customer-integration-settings/` as JSON files (one per customer):

```json
{
  "customer_id": "string",
  "customer_name": "string",
  "district_name": "string",
  "integration_type": "ClassLink|OneRoster|Other",
  "classlink": { ... },
  "oneroster": { ... },
  "ftp": { ... },
  "oneshelf_environment": "staging|production",
  "active": true
}
```

**IMPORTANT:** These files contain references to credentials, not the credentials themselves. Actual credentials are in `.env` or AWS Secrets Manager.

## Development Workflow

### For New Diagnostic Tools

1. **Create task in Kanban**
   ```bash
   # Edit kanban/backlog/TASK-XXX.md
   ```

2. **Implement tool class**
   - Create new file in `src/tools/`
   - Extend `BaseTool` class
   - Implement required methods:
     - `get_inputs()` - Define required inputs
     - `run()` - Execute diagnostic logic
     - `get_status()` - Determine issue status
     - `get_remediation()` - Suggest fixes

3. **Add route**
   - Update `src/routes/tools.py`
   - Create template in `src/templates/tools/`

4. **Write tests**
   - Add test file in `tests/test_tools/`
   - Mock external API calls
   - Test all status conditions

5. **Update documentation**
   - Add tool to README.md
   - Update USER_GUIDE.md

### For New Connectors

1. Create connector class in `src/connectors/`
2. Implement connection, authentication, and data retrieval methods
3. Add configuration to `.env.example`
4. Write integration tests
5. Document in ARCHITECTURE.md

## Important File Locations

### Project Planning
- `PROJECT_REQUIREMENTS.md` - **Complete requirements specification (START HERE)**
- `docs/EXECUTIVE_SUMMARY.html` - Visual overview with diagrams
- `docs/ARCHITECTURE.md` - System architecture details
- `docs/DEPLOYMENT_GUIDE.md` - AWS deployment instructions

### Configuration
- `.env.example` - Environment variables template
- `customer-integration-settings/template.json` - Customer config template

### Kanban
- `kanban/` - Markdown-based task management
- `kanban_server.js` - Kanban UI server
- `kanban_ui.html` - Visual kanban board

## Common Tasks

### Add Support for New Customer

1. Create customer config file in `customer-integration-settings/`
2. Use template.json as starting point
3. Add credentials to `.env` (never in config file)
4. Test connection: `python scripts/test_connections.py --customer <customer_id>`

### Add New Integration Type

1. Create connector in `src/connectors/`
2. Update `customer.py` model to support new type
3. Add configuration fields to customer template
4. Update `.env.example` with new credentials
5. Write integration tests

### Debug Connection Issues

1. Check logs: `tail -f logs/app.log`
2. Test connection: `python scripts/test_connections.py`
3. Verify credentials in `.env`
4. Check customer config in `customer-integration-settings/`
5. Review connector implementation for error handling

### Test Diagnostic Tool

1. Create test customer config with known issue
2. Run tool via UI or direct Python:
   ```python
   from src.tools.student_mismatch import StudentMismatchTool
   tool = StudentMismatchTool(customer_id="test-customer")
   result = tool.run(parent_email="test@example.com", student_name="Test Student")
   ```
3. Verify status determination is correct
4. Check remediation suggestions

## Testing Strategy

### Unit Tests (`tests/test_tools/`, `tests/test_connectors/`)
- Test individual components in isolation
- Mock external API calls
- Test error handling

### Integration Tests (`tests/test_routes/`)
- Test Flask routes
- Use test database
- Mock external services

### End-to-End Tests
- Test complete workflows
- Use staging environment
- Verify HubSpot integration

### Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/test_tools/test_student_mismatch.py

# With coverage
pytest --cov=src --cov-report=html

# Watch mode
pytest-watch
```

## Security Guidelines

### Credential Management

1. **NEVER commit credentials to git**
   - Use `.env` for local development
   - Use AWS Secrets Manager for production
   - Reference credentials by name in customer configs

2. **Database access is READ-ONLY**
   - Never modify production data
   - Use separate read-only database users
   - Audit all queries

3. **API rate limiting**
   - Implement backoff/retry logic
   - Cache responses where appropriate
   - Respect API limits

### User Authentication

- Use Flask-Login for session management
- Hash passwords with bcrypt
- Implement session timeout
- Consider 2FA for production access

## Diagnostic Tool Interface

All diagnostic tools must implement:

```python
class BaseTool(ABC):
    def __init__(self, customer_id: str):
        """Initialize with customer integration settings"""
        pass

    @abstractmethod
    def get_inputs(self) -> Dict[str, str]:
        """Return dict of required input fields"""
        pass

    @abstractmethod
    def run(self, **inputs) -> DiagnosticResult:
        """Execute the diagnostic"""
        pass

    @abstractmethod
    def get_status(self, source_data, bookmarked_data) -> str:
        """Determine issue status"""
        # Return one of:
        # - "ISSUE_IN_SOURCE"
        # - "ISSUE_IN_BOOKMARKED"
        # - "NO_ISSUE"
        # - "BOTH_SOURCES_HAVE_ISSUE"
        pass

    @abstractmethod
    def get_remediation(self, status: str) -> List[str]:
        """Return list of remediation steps"""
        pass
```

## Data Flow Patterns

### Pattern 1: Compare Source vs. Bookmarked

```python
# 1. Load customer config
customer = Customer.load(customer_id)

# 2. Get source data
if customer.integration_type == "ClassLink":
    source_data = classlink_connector.get_students(...)
elif customer.integration_type == "OneRoster":
    source_data = oneroster_connector.get_students(...)

# 3. Get Bookmarked data
if customer.oneshelf_environment == "staging":
    bookmarked_data = bookmarked_db.get_students(..., env="staging")
else:
    bookmarked_data = bookmarked_db.get_students(..., env="production")

# 4. Compare
status = self.get_status(source_data, bookmarked_data)

# 5. Generate result
result = DiagnosticResult(
    status=status,
    source_data=source_data,
    bookmarked_data=bookmarked_data,
    remediation=self.get_remediation(status)
)
```

### Pattern 2: HubSpot Ticket Integration

```python
# 1. Get ticket
ticket = hubspot_connector.get_ticket(ticket_id)

# 2. Extract parameters
customer_id = ticket.get_customer_id()
issue_type = ticket.get_issue_type()

# 3. Select tool
tool_class = tool_selector.recommend(issue_type)
tool = tool_class(customer_id)

# 4. Run diagnostic
result = tool.run(**ticket.get_parameters())

# 5. Update ticket
hubspot_connector.add_comment(ticket_id, result.summary())
```

## Kanban Workflow

Tasks are managed in `kanban/` directory using markdown files:

```
kanban/
├── backlog/        - Planned tasks
├── ready/          - Ready to start
├── in_progress/    - Currently working
├── review/         - Needs review
└── done/           - Completed
```

Each task is a markdown file with frontmatter:

```markdown
---
id: TASK-001
title: Implement Student Mismatch Tool
type: feature
priority: high
assignee: agent
---

## Description
[Task description]

## Acceptance Criteria
- [ ] Tool class implemented
- [ ] Tests passing
- [ ] Documentation updated
```

## AWS Deployment

### Lambda Deployment

```bash
# Install dependencies to package
pip install -r requirements.txt -t package/

# Package application
cd package && zip -r ../deployment.zip . && cd ..
zip -g deployment.zip src/ -r

# Deploy
aws lambda update-function-code \
  --function-name customer-data-tools \
  --zip-file fileb://deployment.zip
```

### ECS Fargate Deployment

```bash
# Build Docker image
docker build -t customer-data-tools .

# Tag and push
docker tag customer-data-tools:latest <ecr-url>/customer-data-tools:latest
docker push <ecr-url>/customer-data-tools:latest

# Update service
aws ecs update-service \
  --cluster customer-tools \
  --service customer-data-tools \
  --force-new-deployment
```

## Tips for Claude Code

1. **Always check PROJECT_REQUIREMENTS.md first** - Complete specification is there
2. **Use BaseTool for consistency** - All diagnostic tools extend this class
3. **Mock external APIs in tests** - Never hit real APIs in unit tests
4. **Read-only database access** - All DB connections must be read-only
5. **Secure credentials** - Never commit to git, use `.env` or Secrets Manager
6. **Update Kanban** - Track work in kanban board for visibility
7. **Document new tools** - Update README and USER_GUIDE
8. **Test with real data** - Use anonymized customer data from staging

## Common Patterns

### Loading Customer Config

```python
from src.models.customer import Customer

customer = Customer.load("killeen-isd")
# Returns Customer object with all integration settings
```

### Connecting to Bookmarked Database

```python
from src.connectors.bookmarked_db import BookmarkedDB

db = BookmarkedDB(environment="staging")  # or "production"
students = db.get_students(district_id=123)
```

### Calling ClassLink API

```python
from src.connectors.classlink import ClassLinkConnector

classlink = ClassLinkConnector(customer_config=customer.classlink)
students = classlink.get_students()
```

### Creating Diagnostic Result

```python
from src.models.diagnostic_result import DiagnosticResult

result = DiagnosticResult(
    tool_name="StudentMismatchTool",
    customer_id="killeen-isd",
    status="ISSUE_IN_BOOKMARKED",
    source_data=source_data,
    bookmarked_data=bookmarked_data,
    remediation=["Remove relationship from Bookmarked", "Sync data from source"],
    timestamp=datetime.now()
)
```

## Project History

- Initialized: 2025-10-14
- Based on: SIS Integration System architecture
- Purpose: Customer support diagnostic tools
- Deployment: AWS Lambda or ECS Fargate
- Status: Active Development

This project follows the architectural patterns established in the SIS Integration System, adapted for diagnostic and troubleshooting use cases.

---

For questions or issues, see `docs/ARCHITECTURE.md` or create a task in the Kanban board.
