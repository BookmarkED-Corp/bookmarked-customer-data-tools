# Customer Data Tools - System Architecture

## Overview

The Customer Data Tools system is a Flask-based diagnostic platform designed to help support engineers quickly identify and resolve data discrepancies between SIS systems and the Bookmarked platform.

## Architecture Principles

1. **Read-Only Access**: All connections to production databases are read-only to prevent accidental data modification
2. **Plugin Architecture**: Diagnostic tools are plugins that extend a common base class, making it easy to add new tools
3. **Environment Isolation**: Separate configurations for staging and production environments
4. **Security First**: Credentials managed through AWS Secrets Manager, all communication encrypted
5. **Extensibility**: Easy to add new integration types, tools, and data sources

## System Components

### 1. Web Application Layer (Flask)

#### Routes (`src/routes/`)
- **`dashboard.py`** - Main dashboard with quick stats and recent diagnostics
- **`tools.py`** - Diagnostic tool selection and execution
- **`settings.py`** - Credential and configuration management
- **`hubspot.py`** - HubSpot OAuth and ticket integration

#### Templates (`src/templates/`)
- Jinja2 templates for all UI components
- Responsive design (Bootstrap-based)
- Component structure:
  - `base.html` - Base template with navigation
  - `dashboard.html` - Dashboard view
  - `tools/` - Tool-specific templates
  - `settings/` - Settings pages

### 2. Authentication Layer (`src/auth/`)

#### User Authentication
- Flask-Login for session management
- Bcrypt for password hashing
- Session timeout: 60 minutes (configurable)
- Optional 2FA for production access

#### Authorization
- Role-based access control
- Separate permissions for:
  - Staging environment access
  - Production environment access
  - Configuration management
  - HubSpot integration

### 3. Data Connector Layer (`src/connectors/`)

#### Bookmarked Connectors
- **`bookmarked_api.py`** - REST API client for Bookmarked backend
  - Methods: `get_students()`, `get_classes()`, `get_enrollments()`, `get_organizations()`
  - Supports both staging and production environments
  - Connection pooling and retry logic

- **`bookmarked_db.py`** - Direct PostgreSQL queries
  - Read-only connection
  - Connection pooling (SQLAlchemy)
  - Query methods for common data patterns
  - Environment selection (staging/production)

#### SIS Connectors
- **`classlink.py`** - ClassLink API integration
  - OAuth2 authentication flow
  - OneRoster 1.1/1.2 data retrieval
  - Rate limiting and backoff
  - Methods: `get_students()`, `get_classes()`, `get_enrollments()`, `get_orgs()`

- **`oneroster.py`** - OneRoster API and CSV parsing
  - Direct OneRoster API support
  - CSV file parsing (ZIP, CSV, XLSX)
  - Manifest file validation
  - Schema validation (OneRoster 1.1 and 1.2)

- **`ftp_client.py`** - FTP server access
  - Per-customer FTP configurations
  - File download and caching
  - Secure credential handling

#### HubSpot Connector
- **`hubspot.py`** - HubSpot API integration
  - OAuth2 flow for bearer token
  - Token refresh handling
  - Methods: `get_ticket()`, `add_comment()`, `update_ticket()`
  - Ticket parsing for auto-populating tool inputs

### 4. Diagnostic Tools Layer (`src/tools/`)

#### Base Tool Class (`base_tool.py`)

```python
class BaseTool(ABC):
    def __init__(self, customer_id: str):
        """Load customer integration settings"""
        self.customer = Customer.load(customer_id)
        self.source_connector = self._init_source_connector()
        self.bookmarked_connector = self._init_bookmarked_connector()

    @abstractmethod
    def get_inputs(self) -> Dict[str, str]:
        """Define required input fields"""
        pass

    @abstractmethod
    def run(self, **inputs) -> DiagnosticResult:
        """Execute diagnostic"""
        pass

    @abstractmethod
    def get_status(self, source_data, bookmarked_data) -> str:
        """Determine issue status"""
        pass

    @abstractmethod
    def get_remediation(self, status: str) -> List[str]:
        """Generate remediation steps"""
        pass
```

#### Tool Implementations

**`student_mismatch.py` - Student Mismatch Resolver**
- **Inputs**: parent_email, student_name, district_id
- **Process**:
  1. Query source data for parent-student relationship
  2. Query Bookmarked for same relationship
  3. Compare results
  4. Determine status: `ISSUE_IN_SOURCE`, `ISSUE_IN_BOOKMARKED`, `NO_ISSUE`
- **Output**: DiagnosticResult with status and remediation steps

**`missing_data.py` - Missing Data Finder**
- **Inputs**: student_name (or class_name), school, district_id
- **Process**:
  1. Search source data
  2. Search Bookmarked data
  3. Identify what's missing
  4. Check import logs for errors
- **Output**: List of missing elements with import status

**`parent_conflicts.py` - Parent Email Conflict Detector**
- **Inputs**: parent_email, district_id
- **Process**:
  1. Find all parents with email in source
  2. Find all parents with email in Bookmarked
  3. Check for name mismatches
  4. Identify conflicting student assignments
- **Output**: List of conflicts with resolution suggestions

**`campus_transfer.py` - Campus Transfer Validator**
- **Inputs**: student_name, old_campus, new_campus, district_id
- **Process**:
  1. Check source data for current enrollment
  2. Check Bookmarked for old campus enrollments
  3. Verify proper relationship cleanup
  4. Identify phantom enrollments
- **Output**: Status of transfer and cleanup issues

### 5. Data Models (`src/models/`)

#### Customer Model (`customer.py`)

```python
class Customer:
    customer_id: str
    customer_name: str
    integration_type: str  # ClassLink, OneRoster, Other
    classlink: Optional[ClassLinkConfig]
    oneroster: Optional[OneRosterConfig]
    ftp: Optional[FTPConfig]
    oneshelf_environment: str  # staging or production
    bookmarked_org_id: str
    active: bool

    @classmethod
    def load(cls, customer_id: str) -> Customer:
        """Load from JSON file in customer-integration-settings/"""

    def get_source_connector(self) -> SourceConnector:
        """Return appropriate connector based on integration_type"""
```

#### Diagnostic Result Model (`diagnostic_result.py`)

```python
class DiagnosticResult:
    tool_name: str
    customer_id: str
    timestamp: datetime
    status: str
    source_data: dict
    bookmarked_data: dict
    comparison: dict
    remediation: List[str]
    hubspot_ticket_id: Optional[str]

    def to_dict(self) -> dict:
        """Serialize for API response"""

    def to_hubspot_comment(self) -> str:
        """Format for HubSpot ticket comment"""
```

### 6. Configuration Layer (`src/config/`)

#### Environment Configuration (`environments.py`)

```python
class Config:
    # Flask settings
    SECRET_KEY: str
    DEBUG: bool

    # Staging environment
    STAGING_API_URL: str
    STAGING_DB_*: str

    # Production environment
    PRODUCTION_API_URL: str
    PRODUCTION_DB_*: str

    # External APIs
    CLASSLINK_API_KEY: str
    HUBSPOT_CLIENT_ID: str

    # AWS
    AWS_SECRETS_MANAGER_ENABLED: bool
```

#### Credential Manager (`credentials.py`)

```python
class CredentialManager:
    def get(self, key: str) -> str:
        """Get credential from .env or AWS Secrets Manager"""

    def set(self, key: str, value: str):
        """Store credential (local only)"""

    def test_connection(self, connection_type: str) -> bool:
        """Test database/API connection"""
```

## Data Flow

### Typical Diagnostic Workflow

```
1. User Authentication
   └─> Flask-Login validates session
   └─> Check role permissions

2. Tool Selection
   └─> User selects tool OR imports HubSpot ticket
   └─> If HubSpot ticket: parse and auto-fill inputs

3. Load Customer Config
   └─> Read JSON from customer-integration-settings/
   └─> Validate configuration
   └─> Load credentials

4. Initialize Connectors
   └─> Source connector (ClassLink/OneRoster/FTP)
   └─> Bookmarked connector (API or direct DB)
   └─> Test connections

5. Gather Source Data
   └─> Call source connector methods
   └─> Handle errors (retry, timeout)
   └─> Cache results

6. Gather Bookmarked Data
   └─> Select environment (staging/production)
   └─> Query API or database
   └─> Cache results

7. Run Comparison
   └─> Tool-specific comparison logic
   └─> Determine status
   └─> Generate remediation steps

8. Display Results
   └─> Render result template
   └─> Show source data, Bookmarked data, diff
   └─> Display remediation options

9. Optional: Update HubSpot
   └─> Add diagnostic results as comment
   └─> Update ticket status if resolved
```

### HubSpot Ticket Integration Flow

```
1. User enters HubSpot ticket URL/number
   └─> OAuth2 bearer token retrieved

2. Fetch ticket details
   └─> GET /crm/v3/objects/tickets/{ticketId}
   └─> Parse description and custom fields

3. Extract parameters
   └─> Customer/District: parsed from ticket
   └─> Issue type: classified from description
   └─> Parent/Student details: extracted

4. Recommend tool
   └─> Match issue type to tool
   └─> Display recommendation to user

5. Execute diagnostic
   └─> Auto-populate tool inputs
   └─> Run diagnostic workflow

6. Update ticket
   └─> POST comment with results
   └─> Optional: change ticket status
```

## Security Architecture

### Credential Storage

**Development/Local:**
- `.env` file (gitignored)
- Plain text (local machine only)

**Production:**
- AWS Secrets Manager
- Encrypted at rest
- Access via IAM roles

### Database Access

**Staging:**
- Read-only PostgreSQL user
- Limited to specific tables/views
- Connection timeout: 30 seconds

**Production:**
- Read-only PostgreSQL user
- Additional authentication layer
- Audit logging enabled
- Connection timeout: 15 seconds

### API Security

- All external API calls over HTTPS
- Rate limiting on tool executions (10/min per user)
- Request timeout: 30 seconds
- Retry logic with exponential backoff

### Session Security

- Secure session cookies (HttpOnly, Secure)
- Session timeout: 60 minutes
- CSRF protection (Flask-WTF)
- Password hashing (bcrypt, cost 12)

## Deployment Architecture

### Option 1: AWS Lambda + API Gateway

```
┌─────────────────────┐
│   CloudFront CDN    │ (Static assets)
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│   API Gateway       │ (REST API)
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│   Lambda Function   │ (Flask app via Mangum)
│   - Python 3.9+     │
│   - 512 MB RAM      │
│   - 30s timeout     │
└──────────┬──────────┘
           │
   ┌───────┴───────┐
   │               │
┌──▼──────┐  ┌────▼────┐
│ Secrets │  │   VPC   │
│ Manager │  │(DB Conn)│
└─────────┘  └─────────┘
```

**Pros:**
- Pay only for usage
- Auto-scaling
- No server management

**Cons:**
- Cold start latency (2-5s)
- 15-minute max execution time
- State not persisted between invocations

### Option 2: AWS ECS Fargate

```
┌─────────────────────┐
│ Application Load    │
│     Balancer        │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│   ECS Fargate       │
│   - Flask container │
│   - 1 vCPU, 2GB RAM │
│   - Auto-scaling    │
└──────────┬──────────┘
           │
   ┌───────┴───────┐
   │               │
┌──▼──────┐  ┌────▼────┐
│ Secrets │  │   VPC   │
│ Manager │  │(DB Conn)│
└─────────┘  └─────────┘
```

**Pros:**
- Always warm (no cold starts)
- Longer execution time
- Better for stateful operations

**Cons:**
- Minimum cost even when idle
- More complex setup
- Requires container management

## Database Schema

### Application Database (New Tables)

**`users`** - Application users
- `id` (PK)
- `username`
- `password_hash`
- `role` (admin, support, viewer)
- `created_at`
- `last_login`

**`diagnostic_runs`** - History of diagnostic executions
- `id` (PK)
- `tool_name`
- `customer_id`
- `user_id` (FK)
- `inputs` (JSON)
- `result` (JSON)
- `status`
- `runtime_seconds`
- `created_at`

**`customer_configs_cache`** - Cached customer configurations
- `customer_id` (PK)
- `config` (JSON)
- `last_updated`

## Extensibility

### Adding a New Diagnostic Tool

1. Create new file in `src/tools/`
2. Extend `BaseTool` class
3. Implement required methods:
   - `get_inputs()`
   - `run()`
   - `get_status()`
   - `get_remediation()`
4. Add route in `src/routes/tools.py`
5. Create template in `src/templates/tools/`
6. Register in tool selector
7. Add tests

### Adding a New Integration Type

1. Create connector in `src/connectors/`
2. Extend `SourceConnector` base class
3. Update `Customer` model to support new type
4. Add config fields to customer template
5. Update credential manager
6. Add integration tests

## Monitoring & Observability

### Logging

- Application logs: `logs/app.log`
- Diagnostic runs: `logs/diagnostics.log`
- Security events: `logs/security.log`

### Metrics (CloudWatch)

- Tool execution time
- Tool success/failure rate
- Database connection errors
- API rate limit hits
- User activity

### Alerts

- Database connection failures
- API credential expiration
- Unusual tool failure rate
- Security events (failed logins)

## Performance Considerations

### Caching Strategy

- Customer configs: cache for 1 hour
- Source data: cache for 5 minutes (per customer)
- HubSpot tickets: cache for 10 minutes
- Database query results: no caching (always fresh)

### Connection Pooling

- Database: 5 connections per pool
- API clients: Keep-alive connections
- Timeout: 30 seconds for all connections

### Rate Limiting

- Tool executions: 10 per minute per user
- HubSpot API: Respect HubSpot limits
- Database queries: 100 per minute per user

## Disaster Recovery

### Backup Strategy

- Customer configs: Stored in git (version controlled)
- Diagnostic history: Backed up daily to S3
- User accounts: Backed up daily to S3

### Rollback Plan

- Lambda: Previous version retained
- ECS: Blue/green deployment
- Database schema: Migration rollback scripts

---

**Document Version:** 1.0
**Last Updated:** 2025-10-14
**Status:** Active Development
