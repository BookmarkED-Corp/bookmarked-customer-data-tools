# Customer Data Tools - Quick Context

**Project:** Diagnostic and troubleshooting tools for Bookmarked customer data issues
**Architecture:** Flask web application with diagnostic tool plugins
**Purpose:** Help support engineers quickly identify and resolve data discrepancies between SIS systems and Bookmarked platform

## Core Components

### Diagnostic Flow
```
User Authentication → Tool Selection → Data Gathering (Source + Bookmarked) → Comparison → Results + Remediation
```

### Key Modules
- **Connectors** (`src/connectors/`) - Data source integrations
  - Bookmarked API/DB (staging & production)
  - ClassLink OAuth2 + API
  - OneRoster API/CSV
  - HubSpot API
  - FTP client

- **Tools** (`src/tools/`) - Diagnostic plugins
  - Student Mismatch Resolver
  - Missing Data Finder
  - Parent Email Conflict Detector
  - Campus Transfer Validator

- **Auth** (`src/auth/`) - User authentication and authorization
- **Models** (`src/models/`) - Customer configs, diagnostic results, users
- **Routes** (`src/routes/`) - Flask endpoints

### Customer Integration Settings
- JSON files in `customer-integration-settings/`
- One file per customer with integration configs
- Credentials referenced from `.env` or AWS Secrets Manager

## Quick Commands

### Development
```bash
# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Edit with your credentials

# Run Flask app (when implemented)
flask run

# Run tests (when implemented)
pytest
pytest --cov=src
```

### Kanban Board
```bash
npm install              # Install Node dependencies
npm start                # Start Kanban server
# Then open: http://localhost:9001/kanban_ui.html

# Or use CLI
python kanban/kanban.py show
```

### Git
```bash
git status
git log --oneline
```

## Important Files
- `PROJECT_REQUIREMENTS.md` - **START HERE** - Complete requirements
- `CLAUDE.md` - Comprehensive AI assistant guide
- `README.md` - Project overview and quick start
- `docs/EXECUTIVE_SUMMARY.html` - Visual project overview
- `docs/ARCHITECTURE.md` - System architecture details
- `kanban/TASK_SUMMARY.md` - All 40 tasks breakdown
- `kanban/PHASE_OVERVIEW.md` - Phase visualization

## Current Status
- Phase: Project Setup Complete ✅
- Next: Phase 1 - Foundation (TASK-001 to TASK-010)
- Tasks: 40 tasks created across 4 phases
- Estimated: 238 hours
- Timeline: 17 days (Oct 14 - Oct 31, 2025)
- Target Launch: October 31, 2025

## Diagnostic Tools

### 1. Student Mismatch Resolver
**Use Case:** Incorrect student assigned to parent account
**Status:** ISSUE_IN_SOURCE | ISSUE_IN_BOOKMARKED | NO_ISSUE

### 2. Missing Data Finder
**Use Case:** Student/class/enrollment missing from Bookmarked
**Checks:** Source data → Bookmarked data comparison

### 3. Parent Email Conflict Detector
**Use Case:** Multiple parents with same email causing overwrites
**Focus:** FERPA compliance and data integrity

### 4. Campus Transfer Validator
**Use Case:** Student transferred campuses, old data not cleaned up
**Checks:** Phantom enrollments, relationship cleanup

## Architecture Principles
1. **Read-Only Access** - All database connections are read-only
2. **Plugin Architecture** - Easy to add new diagnostic tools
3. **Environment Isolation** - Separate staging and production configs
4. **Security First** - Credentials in AWS Secrets Manager
5. **Extensibility** - Easy to add new integration types

## Tech Stack
- **Backend:** Python 3.9+ with Flask
- **Database:** PostgreSQL (read-only to Bookmarked DBs)
- **Frontend:** HTML/CSS/JavaScript (Jinja2 templates)
- **Auth:** Flask-Login, bcrypt
- **Deployment:** AWS Lambda or ECS Fargate
- **APIs:** ClassLink, OneRoster, HubSpot
- **Task Management:** Markdown-based Kanban + Node.js web UI

## Development Workflow

### Adding a New Diagnostic Tool
1. Create tool class in `src/tools/` extending `BaseTool`
2. Implement: `get_inputs()`, `run()`, `get_status()`, `get_remediation()`
3. Add route in `src/routes/tools.py`
4. Create template in `src/templates/tools/`
5. Write tests in `tests/test_tools/`
6. Update documentation

### Adding a New Customer
1. Copy `customer-integration-settings/template.json`
2. Fill in customer details
3. Add credentials to `.env` (use references in JSON)
4. Test connection: `python scripts/test_connections.py --customer <id>`

## Next Steps (Phase 1)
1. TASK-001: Flask application setup
2. TASK-002: Authentication system
3. TASK-003: Bookmarked staging DB connector
4. TASK-004: Bookmarked production DB connector
5. TASK-005: Customer integration settings loader
6. TASK-006: Base diagnostic tool class
7. TASK-007: Credential manager
8. TASK-008: Basic dashboard UI
9. TASK-009: Tool selection UI
10. TASK-010: Phase 1 integration tests

## Security Notes
- **Production access:** Extra authentication layer required
- **Credentials:** Never commit to git, use `.env` or Secrets Manager
- **Database:** Read-only users only
- **Sessions:** 60-minute timeout
- **Logging:** All data access audited

---
*For complete details, read CLAUDE.md and PROJECT_REQUIREMENTS.md in project root*
