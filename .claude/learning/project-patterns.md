# Customer Data Tools - Project Patterns & Knowledge

This file tracks key patterns, decisions, and learnings for this project.

## Project Structure Patterns

### Based on SIS Integration System
This project follows the organizational patterns established in the SIS Integration System:
- Comprehensive documentation (requirements, architecture, executive summary)
- Kanban-based task management with markdown files
- Clear separation of concerns (connectors, tools, models, routes)
- Git repository from the start
- `.claude/` folder for context and learning

### Directory Organization
```
customer-data-tools/
├── .claude/                    # Claude Code context
│   ├── context.md              # Quick reference
│   └── learning/               # Project patterns & knowledge
├── docs/                       # Documentation
├── src/                        # Application source
├── customer-integration-settings/  # Customer configs
├── kanban/                     # Task management
└── tests/                      # Test suite
```

## Key Design Patterns

### 1. Plugin Architecture for Diagnostic Tools
All diagnostic tools extend `BaseTool` abstract class:
- `get_inputs()` - Define required parameters
- `run()` - Execute diagnostic logic
- `get_status()` - Determine issue location (source vs. Bookmarked)
- `get_remediation()` - Generate fix suggestions

**Benefits:**
- Easy to add new tools
- Consistent interface
- Testable in isolation
- Self-documenting

### 2. Environment Abstraction
Support both staging and production with same code:
- Database connections configured via environment
- API endpoints switchable
- Credentials managed per environment
- No hard-coded environment assumptions

### 3. Customer Configuration Pattern
Customer settings stored as JSON files:
- One file per customer
- Credentials referenced, not stored directly
- Version controlled (safe to commit)
- Schema documented in template

**Pattern:**
```json
{
  "customer_id": "example",
  "integration_type": "ClassLink|OneRoster|Other",
  "classlink": { "tenant_id": "...", "oauth_ref": "ENV_VAR" },
  "oneroster": { "api_url": "...", "client_id_ref": "ENV_VAR" },
  "oneshelf_environment": "staging|production"
}
```

### 4. Connector Pattern
All data source connectors implement common interface:
- Connection initialization with credentials
- Authentication handling (OAuth2, API keys)
- Data retrieval methods (get_students, get_classes, etc.)
- Error handling and retry logic
- Connection pooling where appropriate

### 5. Diagnostic Result Pattern
Standard result format for all tools:
```python
DiagnosticResult(
    tool_name="StudentMismatchTool",
    customer_id="killeen-isd",
    status="ISSUE_IN_SOURCE|ISSUE_IN_BOOKMARKED|NO_ISSUE",
    source_data={...},
    bookmarked_data={...},
    comparison={...},
    remediation=["Step 1", "Step 2"],
    timestamp=datetime.now()
)
```

## Deployment Patterns

### AWS Deployment Options

**Option 1: Lambda + API Gateway (Recommended for low usage)**
- Serverless, pay-per-use
- Cold starts acceptable for diagnostic tools
- Mangum adapter for Flask
- AWS Secrets Manager for credentials

**Option 2: ECS Fargate (For higher usage)**
- Always-warm containers
- Better for long-running diagnostics
- More predictable performance
- Higher baseline cost

### Security Patterns

1. **Read-Only Database Access**
   - Separate database users with SELECT-only permissions
   - No INSERT, UPDATE, DELETE ever
   - Connection strings clearly marked as read-only

2. **Credential Management**
   - Development: `.env` file (gitignored)
   - Production: AWS Secrets Manager
   - Reference pattern: `{service}_{env}_{credential_type}`
   - Example: `BOOKMARKED_PROD_DB_PASSWORD`

3. **Authentication Layers**
   - Application auth: Flask-Login
   - Production access: Additional approval/2FA
   - API keys: Per-integration credentials
   - Session management: 60-minute timeout

## Testing Patterns

### Test Organization
```
tests/
├── conftest.py              # Shared fixtures
├── test_connectors/         # Connector tests (mocked APIs)
├── test_tools/              # Tool tests (mocked connectors)
└── test_routes/             # Flask route tests
```

### Mock Pattern
- Mock external APIs (ClassLink, OneRoster, HubSpot)
- Mock database queries
- Use real customer config files (with test credentials)
- Validate result format, not just success/failure

## HubSpot Integration Patterns

### OAuth2 Flow
1. User clicks "Connect HubSpot"
2. Redirect to HubSpot OAuth2 endpoint
3. Callback receives code
4. Exchange code for bearer token
5. Store token in session (or database for persistence)

### Ticket Parsing
Extract structured data from HubSpot tickets:
- Customer/District from ticket properties
- Issue type from description classification
- Parent/Student details from custom fields
- Priority from ticket priority

### Tool Recommendation
Map issue types to tools:
- "wrong student" → StudentMismatchTool
- "missing class" → MissingDataTool
- "duplicate parent" → ParentConflictTool
- "transfer issue" → CampusTransferTool

## UI/UX Patterns

### Dashboard Layout
1. Quick stats (tickets processed, common issues)
2. Recent diagnostics
3. Quick access to tools
4. HubSpot ticket input

### Tool Execution Flow
1. Select tool (or auto-select from HubSpot ticket)
2. Input form (pre-filled if from ticket)
3. Progress indicator during execution
4. Results display with clear status
5. Remediation steps
6. Optional: Update HubSpot ticket

### Results Display Pattern
```
┌─────────────────────────────────────┐
│ Status: ISSUE_IN_SOURCE             │
├─────────────────────────────────────┤
│ Source Data (ClassLink)             │
│ [Data display]                      │
├─────────────────────────────────────┤
│ Bookmarked Data (Production)        │
│ [Data display]                      │
├─────────────────────────────────────┤
│ Comparison                          │
│ [Diff display]                      │
├─────────────────────────────────────┤
│ Remediation Steps                   │
│ 1. Fix in ClassLink                 │
│ 2. Re-sync data                     │
└─────────────────────────────────────┘
```

## Documentation Patterns

### Multi-Format Documentation
- **Markdown** - Technical docs, requirements, architecture
- **HTML** - Executive summary, visual overviews
- **Inline** - Code comments and docstrings
- **Kanban** - Task-level documentation

### Documentation Hierarchy
1. **Quick Context** - `.claude/context.md` (this file's parent)
2. **Overview** - `README.md`
3. **Requirements** - `PROJECT_REQUIREMENTS.md`
4. **Architecture** - `docs/ARCHITECTURE.md`
5. **Visual Summary** - `docs/EXECUTIVE_SUMMARY.html`
6. **AI Guide** - `CLAUDE.md`

## Kanban Patterns

### Task Organization
- **Backlog** - All planned tasks
- **Ready** - Prerequisites met, ready to start
- **In Progress** - Currently being worked on
- **Review** - Code complete, needs review
- **Done** - Completed and verified

### Task File Format
Markdown with YAML frontmatter:
```yaml
---
id: TASK-001
title: Task title
type: feature|bug|docs|test
priority: critical|high|medium|low
assignee: agent|human|unassigned
phase: 1|2|3|4
estimated_hours: X
---

## Description
[Details]

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Dependencies
- TASK-XXX

## Notes
[Additional info]
```

## Code Organization Patterns

### Flask Application Structure
```python
# src/app.py - Application factory
def create_app(config=None):
    app = Flask(__name__)

    # Load config
    app.config.from_object(config or Config)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Register blueprints
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(tools_bp)
    app.register_blueprint(settings_bp)

    return app
```

### Connector Pattern
```python
# src/connectors/base.py
class BaseConnector(ABC):
    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def get_students(self, **filters):
        pass

    @abstractmethod
    def get_classes(self, **filters):
        pass
```

## Lessons from SIS Integration System

### What Worked Well
1. **Comprehensive upfront documentation** - Clear requirements prevented rework
2. **Kanban task management** - Visual board + markdown files = no conflicts
3. **Multi-format docs** - HTML summary for stakeholders, MD for developers
4. **CLAUDE.md** - Single source of truth for AI development
5. **Git from day 1** - Version control for everything including docs

### Applied to This Project
- Similar documentation structure
- Same Kanban system (markdown + Node.js UI)
- Comprehensive requirements before coding
- Clear architecture documentation
- `.claude/` folder for context and learning

## Future Patterns to Consider

### Phase 2 Enhancements
- Automated remediation (with approval workflow)
- Bulk diagnostic runs
- Historical trending
- Integration with alerting systems

### Phase 3 Potential Patterns
- ML-based ticket classification
- Predictive issue detection
- Customer health scoring
- Proactive monitoring integration

---

**Last Updated:** October 14, 2025
**Status:** Project Setup Complete
**Next Phase:** Phase 1 - Foundation
