# Customer Data Tools - Project Requirements

## Executive Summary

The **Customer Data Tools** project is a Flask-based web application designed to diagnose, debug, and resolve customer data issues in the Bookmarked platform. This tool provides a centralized interface for accessing customer integration data, troubleshooting common issues, and managing connections to multiple data sources including SIS systems, Bookmarked APIs, and HubSpot.

**Target Deployment:** AWS Cloud Service (Low-usage pattern - serverless or container-based)

## Project Overview

### Purpose
Streamline the process of diagnosing and resolving customer data issues by providing:
- Centralized access to customer integration configurations
- Tools for comparing source data vs. production data
- Automated diagnostics for common data issues
- Direct integration with HubSpot for ticket tracking

### Key Stakeholders
- Customer Support Team
- Technical Support Engineers
- Integration Specialists
- Development Team

## Core Requirements

### 1. Database Connectivity

#### Bookmarked Backend API & Database
- **Staging Environment**
  - Read-only connection to staging API
  - Read-only connection to staging PostgreSQL database
  - Credential management via environment variables

- **Production Environment**
  - Read-only connection to production API
  - Read-only connection to production PostgreSQL database
  - Additional security controls for production access

- **Dynamic Configuration**
  - Allow switching between staging and production targets
  - Support for adding new connection strings via UI
  - Store credentials in `.env` or deployable config files
  - Validate connections before use

#### Customer Source Data Access
- **ClassLink Integration**
  - OAuth2 authentication flow
  - API credentials: `a09d52aa-1480-405d-80bc-aa3ac120a38c` (pending approval)
  - Support for ClassLink API v2
  - OneRoster 1.1/1.2 data retrieval

- **OneRoster Integration**
  - Direct OneRoster API access
  - CSV file upload and parsing
  - FTP server connectivity (customer-specific)

- **FTP Server Access**
  - Per-customer FTP configuration
  - Credential storage in customer integration settings
  - Secure credential handling

### 2. Customer Integration Settings

#### Storage Format
- JSON files in `customer-integration-settings/` folder
- One file per customer organization
- Version-controlled alongside application code

#### Required Fields per Customer
```json
{
  "customer_id": "string",
  "customer_name": "string",
  "district_name": "string",
  "integration_type": "ClassLink|OneRoster|Other",

  "classlink": {
    "enabled": true,
    "tenant_id": "string",
    "oauth_credentials": "reference_to_secure_store"
  },

  "oneroster": {
    "enabled": true,
    "api_url": "string",
    "api_key": "reference_to_secure_store",
    "csv_upload": true
  },

  "ftp": {
    "enabled": true,
    "host": "string",
    "port": 21,
    "username": "string",
    "password": "reference_to_secure_store",
    "path": "/data"
  },

  "oneshelf_environment": "staging|production",
  "bookmarked_org_id": "string",
  "active": true,
  "notes": "string"
}
```

### 3. HubSpot Integration

#### Authentication
- OAuth2 flow for obtaining bearer token
- Token refresh handling
- Store token securely per user session

#### Functionality
- Pull ticket information by ticket number or URL
- Display ticket details in tool interface
- Link diagnostic results to HubSpot tickets
- Auto-populate ticket fields with diagnostic findings

### 4. Application Access Control

#### Authentication
- Username/password authentication for accessing the app
- Separate credential sets for:
  - Staging web app & API access
  - Production web app & API access
  - HubSpot access

#### Credential Management UI
- Centralized "Accounts" or "Settings" section
- Store credentials per integration/environment
- Detect missing credentials and prompt user
- Secure credential storage (encrypted at rest)

### 5. Diagnostic Tools

#### Initial Tool Set

##### Tool 1: Student Mismatch Resolver
**Use Case:** Incorrect student assigned to parent account

**Workflow:**
1. Input: Parent email, student name, district
2. Check source data (ClassLink/OneRoster)
   - Does relationship exist in source?
   - Is student correctly assigned to parent?
3. Check Bookmarked production database
   - Does relationship exist in Bookmarked?
   - Are there phantom relationships?
4. Output status:
   - "ISSUE EXISTS IN SOURCE DATA (ClassLink/OneRoster)"
   - "ISSUE EXISTS IN PROD (Source data OK)"
   - "NO ISSUE FOUND"
5. Provide remediation options:
   - Remove relationship from Bookmarked
   - Flag for manual review
   - Update HubSpot ticket with findings

##### Tool 2: Missing Student/Class Data
**Use Case:** Student not showing up in parent account, or classes missing

**Workflow:**
1. Input: Student name, school, district
2. Source data verification
   - Student exists in SIS?
   - Classes assigned in SIS?
   - Teacher assignments correct?
3. Bookmarked data verification
   - Student imported to Bookmarked?
   - Classes created?
   - Enrollments present?
4. Output status and missing elements
5. Remediation suggestions

##### Tool 3: Parent Email Conflicts
**Use Case:** Multiple parents with same email, data overwrite issues

**Workflow:**
1. Input: Parent email, district
2. Source data check
   - How many parents with this email?
   - Are they distinct individuals?
3. Bookmarked data check
   - Parent records in database
   - Student associations
4. Identify conflicts
5. Suggest resolution

##### Tool 4: Campus Transfer Validation
**Use Case:** Student transferred campuses but still shows in old campus

**Workflow:**
1. Input: Student name, old campus, new campus
2. Source data verification
3. Bookmarked relationship cleanup verification
4. Identify phantom enrollments
5. Remediation path

#### Tool Extensibility
- Plugin architecture for adding new diagnostic tools
- Common interface for all tools:
  - Input parameters
  - Data source queries
  - Status determination
  - Remediation suggestions
  - HubSpot integration

### 6. HubSpot Integration Features

#### Ticket Processing
- Parse HubSpot ticket URL or ticket number
- Extract:
  - Customer/District information
  - Issue type
  - Parent/Student details
  - Priority level
- Auto-select appropriate diagnostic tool
- Pre-fill tool inputs from ticket data

#### Tool Suggestion Engine
- Analyze ticket description
- Map to available diagnostic tools
- Suggest tool: "Recommended: Student Mismatch Resolver"
- Or prompt: "Not sure which tool to use for this ticket?"

### 7. User Interface Requirements

#### Layout
- Modern, responsive Flask web application
- Bootstrap or similar CSS framework
- Mobile-friendly design

#### Key Screens

**1. Dashboard**
- Quick stats (tickets processed today, common issues)
- Recent diagnostic runs
- Quick access to common tools

**2. Accounts / Settings**
- Manage all credentials:
  - Staging API (username/password)
  - Production API (username/password)
  - HubSpot OAuth
  - Database connections
- Connection testing
- Credential status indicators

**3. Customer Integration Settings**
- List all customers
- Add/edit customer integration config
- View/test connection to customer source data
- Import/export customer configs

**4. Diagnostic Tools Dashboard (`/tools`)**

**Unified Tools Page Architecture** (Implemented)

This is the main entry point for all diagnostic tools. The page provides a centralized, app-like interface for district selection and tool access.

*Key Features:*

- **Environment Selector**
  - Dropdown to select staging or production environment
  - Selection persists across page navigation
  - Changes environment for both district search and tool execution

- **Searchable District Picker**
  - Real-time search input field (minimum 3 characters required)
  - Search by district name OR district ID
  - Live filtering with autocomplete dropdown
  - Shows first 50 matching results
  - Displays: "Showing first 50 of X matches. Keep typing to narrow down..."
  - Click-to-select from dropdown results
  - Selected district displayed prominently with ID and environment

- **Tool Cards Grid**
  - Visual grid layout of available diagnostic tools
  - Each card shows:
    - Tool icon
    - Tool name
    - Brief description
    - Status badge (Available / Coming Soon)
  - Tools initially shown:
    1. **Student Search** (Available) - Compare student data across systems
    2. Student Mismatch Resolver (Coming Soon)
    3. Missing Data Finder (Coming Soon)
    4. Parent Email Conflicts (Coming Soon)
    5. Campus Transfer Validator (Coming Soon)
    6. Data Quality Report (Coming Soon)

- **Tool Launch Behavior**
  - Tools are disabled until district is selected
  - Clicking enabled tool button:
    - Saves district info to sessionStorage (district_id, district_name, environment)
    - Navigates to tool-specific page
  - Tool pages can link back with "Change District" option

*Technical Implementation:*
- Uses localStorage for district selection persistence
- Uses sessionStorage for passing district info to tool pages
- Implements minimum 3-character search to prevent overwhelming results
- Limits dropdown results to 50 for performance
- All district data fetched from `/api/districts` endpoint

*Navigation Flow:*
```
Dashboard → /tools (select district + tool) → /tools/student-search
                                            ↓
                                "Change District" link returns to /tools
```

**5. HubSpot Ticket Processor**
- Ticket URL/number input
- Ticket details display
- Tool recommendation
- One-click launch of recommended tool

## Technical Architecture

### Application Stack
- **Backend:** Python 3.9+ with Flask
- **Database:** PostgreSQL (read-only connections to existing Bookmarked DBs)
- **Frontend:** HTML/CSS/JavaScript (Jinja2 templates)
- **API Client:** Requests library for external APIs
- **Auth:** Flask-Login for user sessions
- **Deployment:** AWS (Lambda + API Gateway OR ECS Fargate)

### Project Structure (Based on SIS Integration System)
```
customer-data-tools/
├── docs/                           # Documentation
│   ├── EXECUTIVE_SUMMARY.html      # Executive summary
│   ├── ARCHITECTURE.md             # System architecture
│   ├── DEPLOYMENT_GUIDE.md         # AWS deployment guide
│   └── USER_GUIDE.md               # End-user documentation
├── src/                            # Application source code
│   ├── app.py                      # Flask application entry point
│   ├── config/                     # Configuration management
│   │   ├── __init__.py
│   │   ├── environments.py         # Environment configs
│   │   └── credentials.py          # Credential handling
│   ├── auth/                       # Authentication
│   │   ├── __init__.py
│   │   ├── login.py
│   │   └── middleware.py
│   ├── connectors/                 # Data source connectors
│   │   ├── __init__.py
│   │   ├── bookmarked_api.py       # Bookmarked API client
│   │   ├── bookmarked_db.py        # Direct DB queries
│   │   ├── classlink.py            # ClassLink API
│   │   ├── oneroster.py            # OneRoster API/CSV
│   │   ├── hubspot.py              # HubSpot API
│   │   └── ftp_client.py           # FTP access
│   ├── tools/                      # Diagnostic tools
│   │   ├── __init__.py
│   │   ├── base_tool.py            # Base class for all tools
│   │   ├── student_mismatch.py     # Student mismatch resolver
│   │   ├── missing_data.py         # Missing student/class data
│   │   ├── parent_conflicts.py     # Parent email conflicts
│   │   └── campus_transfer.py      # Campus transfer validator
│   ├── models/                     # Data models
│   │   ├── __init__.py
│   │   ├── customer.py             # Customer integration settings
│   │   ├── diagnostic_result.py    # Diagnostic run results
│   │   └── user.py                 # Application users
│   ├── routes/                     # Flask routes
│   │   ├── __init__.py
│   │   ├── dashboard.py
│   │   ├── tools.py
│   │   ├── settings.py
│   │   └── hubspot.py
│   ├── templates/                  # Jinja2 templates
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── tools/
│   │   ├── settings/
│   │   └── hubspot/
│   └── static/                     # CSS, JS, images
│       ├── css/
│       ├── js/
│       └── img/
├── customer-integration-settings/  # Customer configs (JSON)
├── tests/                          # Unit and integration tests
│   ├── conftest.py
│   ├── test_connectors/
│   ├── test_tools/
│   └── test_routes/
├── scripts/                        # Utility scripts
│   ├── init_db.py
│   ├── import_customers.py
│   └── test_connections.py
├── kanban/                         # Kanban board for task management
│   ├── backlog/
│   ├── ready/
│   ├── in_progress/
│   ├── review/
│   ├── done/
│   └── kanban.py
├── .env.example                    # Environment variables template
├── .env                            # Local environment (gitignored)
├── .gitignore
├── requirements.txt                # Python dependencies
├── README.md
├── CLAUDE.md                       # Claude Code guidance
└── kanban_server.js                # Kanban UI server
```

### AWS Deployment Options

#### Option 1: AWS Lambda + API Gateway (Recommended for low usage)
- **Pros:**
  - Pay only for usage
  - Automatic scaling
  - No server management
- **Cons:**
  - Cold start latency
  - 15-minute execution limit
- **Best for:** Infrequent usage, < 100 requests/day

#### Option 2: AWS ECS Fargate
- **Pros:**
  - Container-based
  - Always warm
  - Better for longer-running operations
- **Cons:**
  - Minimum cost even when idle
  - More complex setup
- **Best for:** Regular usage, multiple concurrent users

#### Option 3: AWS Lightsail
- **Pros:**
  - Simple, predictable pricing
  - Easy to set up
  - Good for small apps
- **Cons:**
  - Fixed resources
  - Manual scaling
- **Best for:** Dedicated small instance, predictable workload

### Security Considerations

1. **Credential Storage**
   - Use AWS Secrets Manager or Parameter Store
   - Never commit credentials to git
   - Encrypt at rest
   - Rotate regularly

2. **Database Access**
   - Read-only database users
   - Limit to specific tables/views
   - Connection pooling with timeouts
   - Audit logging

3. **API Access**
   - Rate limiting
   - Request timeout
   - Error handling (don't leak internal details)
   - HTTPS only

4. **User Authentication**
   - Password hashing (bcrypt)
   - Session management
   - Optional: 2FA for production access
   - Session timeout

## Data Flow

### Typical Diagnostic Workflow

```
User Login
    ↓
Select Tool (or Import HubSpot Ticket)
    ↓
Enter Parameters (or Auto-fill from ticket)
    ↓
Tool Execution:
    1. Fetch customer integration settings
    2. Connect to source data (ClassLink/OneRoster/FTP)
    3. Query source data
    4. Connect to Bookmarked (staging or prod)
    5. Query Bookmarked database/API
    6. Compare results
    7. Determine status
    8. Generate remediation suggestions
    ↓
Display Results
    ↓
Optional: Update HubSpot ticket
    ↓
Optional: Execute remediation
```

## Success Criteria

### Technical Metrics
- All diagnostic tools return results in < 30 seconds
- Database connection success rate > 99%
- Zero credential leaks or security incidents
- Support for all active customer integration types

### Business Metrics
- Reduce average ticket resolution time by 50%
- 80% of common issues diagnosable without manual database queries
- 100% of customer integration configs documented
- Support team adoption > 90%

## Risks & Mitigation

### Risk: Production Database Access
**Mitigation:**
- Read-only credentials
- Audit all production queries
- Require additional auth for production access
- Rate limiting

### Risk: Credential Management
**Mitigation:**
- Use AWS Secrets Manager
- Credential rotation
- Least privilege principle
- Regular security audits

### Risk: Tool Accuracy
**Mitigation:**
- Comprehensive testing with real customer data
- Validation against known issues
- Clear confidence indicators in results
- Manual review option

### Risk: HubSpot API Rate Limits
**Mitigation:**
- Cache ticket data
- Implement backoff/retry logic
- Request batching where possible

## Future Enhancements

### Phase 2
- Automated remediation (with approval workflow)
- Bulk diagnostic runs
- Historical trending of issues
- Integration with alerting systems

### Phase 3
- Machine learning for ticket classification
- Predictive issue detection
- Customer health dashboard
- Integration with monitoring tools

## Development Timeline

See `docs/PROJECT_TIMELINE.md` for detailed phased implementation plan.

## References

- SIS Integration System: `/Users/ryan-bookmarked/platform/bookmarked/bookmarked-experimental/sis-integration-system`
- Bookmarked Backend API Documentation: [Internal Link]
- ClassLink API Docs: https://developer.classlink.com/
- OneRoster API Docs: https://www.imsglobal.org/activity/onerosterlis
- HubSpot API Docs: https://developers.hubspot.com/

---

**Document Version:** 1.0
**Last Updated:** 2025-10-14
**Status:** Draft for Review
